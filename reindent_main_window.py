"""
main_window.py Re-Indentation Motoru v2
=========================================
Duzeltmeler:
- paren_depth kontrolu known-value kontrolunden ONCE
- Genel None satirlar icin nk (sonraki bilinen) kullanilir
- Kapama parantezi/kose/kume ozel islenir
- 4-space indent (orijinal dosya standardi)
"""

import marshal, dis, struct, sys, py_compile, os

PYC = r'E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\__pycache__\main_window.cpython-311.pyc'
PY  = r'E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\main_window.py'
OUT = r'E:\İNŞAAT METRAJ PRO\main_window_fixed.py'
LOG = r'E:\İNŞAAT METRAJ PRO\reindent_log.txt'

INDENT_SIZE = 4

results = []
def log(msg):
    results.append(msg)

# ===================================================================
# 1. .pyc yukle
# ===================================================================
log("ADIM 1: .pyc yukleniyor")
with open(PYC, 'rb') as f:
    f.read(16)
    root_code = marshal.load(f)
log("  OK")

# ===================================================================
# 2. line_min_col: instr.positions.col_offset ile
# ===================================================================
log("ADIM 2: Bytecode pozisyonlari okunuyor")
line_min_col = {}

# Python 3.11'de RESUME ve COPY_FREE_VARS prolog komutlari col=0 ile
# gelir ve gercek indent bilgisini bozar. Bu komutlari atla.
SKIP_OPCODES = frozenset({'RESUME', 'COPY_FREE_VARS', 'MAKE_CELL'})

# Lambda/comprehension gibi anonim code objectlerin col=0 komutlari
# (ornegin RETURN_VALUE) sentetik olup gercek pozisyon tasimaz.
ANON_CODE_NAMES = frozenset({'<lambda>', '<listcomp>', '<dictcomp>', '<setcomp>', '<genexpr>'})

def walk_positions(c):
    cname = getattr(c, 'co_name', '?')
    is_anon = cname in ANON_CODE_NAMES
    for instr in dis.get_instructions(c):
        if instr.opname in SKIP_OPCODES:
            continue  # Prolog komutlari col=0 verir, atla
        pos = getattr(instr, 'positions', None)
        if pos and pos.lineno is not None and pos.col_offset is not None:
            ln, col = pos.lineno, pos.col_offset
            # Anonim code object'ten gelen col=0 komutlari atla
            # (lambda/comprehension RETURN_VALUE col=0 verir, yanlis min yapar)
            if is_anon and col == 0:
                continue
            if ln not in line_min_col or col < line_min_col[ln]:
                line_min_col[ln] = col
    for const in c.co_consts:
        if hasattr(const, 'co_code'):
            walk_positions(const)

walk_positions(root_code)
log(f"  {len(line_min_col)} satir haritada")

# ===================================================================
# 3. def/class satirlari icin depth-bazli indent
# ===================================================================
log("ADIM 3: def/class depth haritasi")
defclass_indent = {}

def walk_code_objects(c, depth=0):
    if depth > 0:
        fl = c.co_firstlineno
        correct = (depth - 1) * INDENT_SIZE
        if fl not in defclass_indent or defclass_indent[fl] < correct:
            defclass_indent[fl] = correct
    for const in c.co_consts:
        if hasattr(const, 'co_code'):
            walk_code_objects(const, depth + 1)

walk_code_objects(root_code, 0)
log(f"  {len(defclass_indent)} def/class satiri")

# ===================================================================
# 4. Kaynak oku
# ===================================================================
log("ADIM 4: Kaynak okunuyor")
with open(PY, 'r', encoding='utf-8') as f:
    raw_lines = f.readlines()
n = len(raw_lines)
log(f"  {n} satir")

# ===================================================================
# 5. known[lineno]: kesin bilinen indent degerleri
#    NOT: parantez icindeki satirlarin bilinen degeri KULLANILMAZ
#         (parantez takibine gore override edilir)
# ===================================================================
known = {}

for lno, raw in enumerate(raw_lines, 1):
    stripped_c = raw.strip()
    if not stripped_c:
        known[lno] = None
        continue

    is_dc = (stripped_c.startswith('def ') or
             stripped_c.startswith('class ') or
             stripped_c.startswith('async def '))

    # 'elif' icin bytecode kondisyon kolonu yanilticidir (keyword degil
    # kondisyonun kolununu verir). Heuristic (nk - INDENT_SIZE) daha guvenilir.
    if stripped_c.startswith('elif ') or stripped_c.startswith('elif\t'):
        known[lno] = None
        continue

    if is_dc and lno in defclass_indent:
        dc_val = defclass_indent[lno]
        # MAKE_FUNCTION pozisyonu, def'in if/for blogu icinde oldugunda
        # (depth-1)*4'ten daha derin bir indent verir. Her ikisinin maksimumunu al.
        if lno in line_min_col:
            bc_col = (line_min_col[lno] // INDENT_SIZE) * INDENT_SIZE
            known[lno] = max(dc_val, bc_col)
        else:
            known[lno] = dc_val
    elif lno in line_min_col:
        col = line_min_col[lno]
        # 4-space multiple'a yuvarla
        col = (col // INDENT_SIZE) * INDENT_SIZE
        if col == 0 and is_dc and lno in defclass_indent:
            known[lno] = defclass_indent[lno]
        else:
            known[lno] = col
    else:
        known[lno] = None

known_count = sum(1 for v in known.values() if v is not None)
log(f"  Bilinen: {known_count}/{n} satirlar (%{100*known_count//n})")

# ===================================================================
# 6. next_k ve prev_k on-hesaplama
# ===================================================================
next_k = [None] * (n + 2)
prev_k = [None] * (n + 2)

last = None
for i in range(n, 0, -1):
    if known[i] is not None:
        last = known[i]
    next_k[i] = last

last = None
for i in range(1, n + 1):
    if known[i] is not None:
        last = known[i]
    prev_k[i] = last

# ===================================================================
# 7. Ana gecis: her satir icin dogru indent belirle
#    ONEM: paren_depth kontrolu known-value kontrolunden ONCE
# ===================================================================
log("ADIM 5: Indent atama gecisi")

final_indent = {}

# Parantez takibi
paren_stack = []   # (acilis_char, lineno, acilis_satiri_indent)
paren_depth = 0

def count_brackets(text, cur_paren_depth, cur_paren_stack, line_indent):
    """
    Metindeki parantezleri say.
    String iclerini basit olarak atla (tek/cift tirnak - uclu tirnak hariç).
    Dondur: (yeni_paren_depth, yeni_paren_stack)
    """
    in_str = False
    str_char = None
    i = 0
    while i < len(text):
        ch = text[i]
        if in_str:
            if ch == '\\':
                i += 2
                continue
            elif ch == str_char:
                in_str = False
        else:
            if ch in ('"', "'"):
                # Uclu tirnak kontrolu
                triple = text[i:i+3]
                if triple in ('"""', "'''"):
                    # Uclu tirnak: kapatilana kadar atla (ayni satir icin)
                    end = text.find(triple, i + 3)
                    if end != -1:
                        i = end + 3
                        continue
                    else:
                        # Devam eden uclu tirnak - satir sonuna kadar atla
                        i = len(text)
                        continue
                else:
                    in_str = True
                    str_char = ch
            elif ch in '([{':
                cur_paren_stack.append((ch, line_indent))
                cur_paren_depth += 1
            elif ch in ')]}':
                if cur_paren_stack:
                    cur_paren_stack.pop()
                cur_paren_depth = max(0, cur_paren_depth - 1)
        i += 1
    return cur_paren_depth, cur_paren_stack

DEBUG_RANGE = range(3958, 3982)
debug_lines_out = []

for lno in range(1, n + 1):
    raw = raw_lines[lno - 1]
    stripped = raw.strip()

    if lno in DEBUG_RANGE:
        debug_lines_out.append(
            f"L{lno:4d} pd={paren_depth} ps={[x[1] for x in paren_stack[-3:]]} "
            f"kn={known.get(lno,'?')} | {stripped[:50]}"
        )

    # --- Bos satir ---
    if not stripped:
        final_indent[lno] = -1
        continue

    # --- Oncelik 1: Bytecode bilgisi var (en guvenilir kaynak) ---
    # Kapama parantezi DEGIL ama bilinen indent varsa: bytecode'a guvenir
    if known[lno] is not None and (not stripped or stripped[0] not in ')]}'):
        ind = known[lno]
        # Paren takibinde yanlis sayilmis parantez varsa duzelt:
        # Eger bilinen indent, acilis parantezinin indentinden <= ise
        # o parantez yanlis sayilmis demektir -> temizle
        while paren_stack and ind <= paren_stack[-1][1]:
            paren_stack.pop()
            paren_depth = max(0, paren_depth - 1)
        final_indent[lno] = ind
        paren_depth, paren_stack = count_brackets(stripped, paren_depth, paren_stack, ind)
        continue

    # --- Oncelik 2: Kapama parantezi (paren_depth>0 ise) ---
    if paren_depth > 0 and stripped and stripped[0] in ')]}':
        if paren_stack:
            ind = paren_stack[-1][1]  # acilis satirinin indenti
            paren_stack.pop()
            paren_depth = max(0, paren_depth - 1)
        else:
            ind = max(0, (prev_k[lno] or INDENT_SIZE) - INDENT_SIZE)
            paren_depth = 0
        final_indent[lno] = ind
        rest = stripped[1:]
        if rest:
            paren_depth, paren_stack = count_brackets(rest, paren_depth, paren_stack, ind)
        continue

    # --- Oncelik 3: Parantez icinde devam satiri ---
    if paren_depth > 0:
        if paren_stack:
            ind = paren_stack[-1][1] + INDENT_SIZE
        else:
            ind = (prev_k[lno] or 0) + INDENT_SIZE
        final_indent[lno] = ind
        paren_depth, paren_stack = count_brackets(stripped, paren_depth, paren_stack, ind)
        continue

    # --- Oncelik 4: None satir, paren disinda - akilli tahmin ---
    if stripped == 'else:' or stripped.startswith('else:') or stripped.startswith('else '):
        nk = next_k[lno]
        ind = max(0, (nk if nk is not None else INDENT_SIZE) - INDENT_SIZE)

    elif stripped.startswith('elif ') or stripped.startswith('elif\t'):
        nk = next_k[lno]
        ind = max(0, (nk if nk is not None else INDENT_SIZE) - INDENT_SIZE)

    elif (stripped.startswith('except:') or stripped.startswith('except ')
          or stripped.startswith('except\t') or stripped == 'except:'):
        nk = next_k[lno]
        ind = max(0, (nk if nk is not None else INDENT_SIZE) - INDENT_SIZE)

    elif stripped == 'finally:' or stripped.startswith('finally:'):
        nk = next_k[lno]
        ind = max(0, (nk if nk is not None else INDENT_SIZE) - INDENT_SIZE)

    elif stripped == 'try:' or stripped.startswith('try:'):
        nk = next_k[lno]
        ind = max(0, (nk if nk is not None else INDENT_SIZE) - INDENT_SIZE)

    elif stripped.startswith('#'):
        # Yorum: bir sonraki kod satirinin indenti
        nk = next_k[lno]
        pk = prev_k[lno]
        ind = nk if nk is not None else (pk or 0)

    else:
        # Genel None satir (docstring, kapama parantezi, vs.):
        # Bir sonraki bilinen indent kullan
        nk = next_k[lno]
        pk = prev_k[lno]
        if nk is not None and pk is not None:
            # Hangisi daha derine gidiyorsa tercih et (fonksiyon gövdesi vs. def)
            ind = nk  # Genelde nk daha dogru (docstring icin)
        elif nk is not None:
            ind = nk
        elif pk is not None:
            ind = pk
        else:
            ind = 0

    final_indent[lno] = ind
    paren_depth, paren_stack = count_brackets(stripped, paren_depth, paren_stack, ind)

# ===================================================================
# 8. Ciktiyi yaz
# ===================================================================
log("ADIM 6: Dosya yaziliyor")
with open(OUT, 'w', encoding='utf-8') as f:
    for lno in range(1, n + 1):
        raw = raw_lines[lno - 1]
        stripped = raw.strip()
        eol = '\r\n' if raw.endswith('\r\n') else '\n'

        if not stripped:
            f.write(eol)
            continue

        ind = final_indent.get(lno, 0)
        if ind < 0:
            f.write(eol)
        else:
            f.write(' ' * ind + stripped + eol)

sz = os.path.getsize(OUT)
log(f"  Yazildi: {OUT} ({sz} bytes)")

with open(r'E:\İNŞAAT METRAJ PRO\debug_paren.txt', 'w', encoding='utf-8') as _df:
    _df.write('\n'.join(debug_lines_out))

# ===================================================================
# 9. Syntax dogrulama
# ===================================================================
log("ADIM 7: Syntax dogrulamasi")
try:
    py_compile.compile(OUT, doraise=True)
    log(">>> SYNTAX GECERLI - BASARILI!")
except py_compile.PyCompileError as e:
    log(f"SYNTAX HATASI: {e}")
    import re
    m = re.search(r'line (\d+)', str(e))
    if m:
        eln = int(m.group(1))
        with open(OUT, 'r', encoding='utf-8') as f:
            lns = f.readlines()
        log(f"  Hata satiri {eln} civari:")
        for i in range(max(1, eln-3), min(len(lns)+1, eln+5)):
            marker = " <<<<" if i == eln else ""
            log(f"    L{i}: {repr(lns[i-1][:90])}{marker}")

# Log kaydet
with open(LOG, 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))

# Ekrana da yaz
for line in results:
    print(line)
