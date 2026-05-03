"""
pyc_fix2.py - Pyc col_offset tabanlı indentation duzeltici (v2).

Duzeltilen hatalar (onceki fix_autocad.py'ye gore):
1. MINIMUM col_offset alinir (onceki: ilk bulunan kazanir -> yanlis kod obj)
2. RESUME/COPY_FREE_VARS/MAKE_CELL/CACHE sintetik instructionlar atlandi
3. Tum nested code object'ler ozyinelemeli taraniyor (onceki: sadece modul level)
4. 27-satir offset dogru uygulanior (current_line >= 155 -> pyc_line = current-27)
5. Continuation lines (paren icinde) ve comments 1-space'de birakilir -> gecerli Python
"""
import dis, marshal, struct, os, shutil, py_compile, re

PYC  = r"E:\INS AAT METRAJ PRO\yeni_proje\app\core\__pycache__\autocad_connector.cpython-311.pyc".replace("INS AAT", "\u0130N\u015eAAT")
SRC  = r"E:\INS AAT METRAJ PRO\yeni_proje\app\core\autocad_connector.py".replace("INS AAT", "\u0130N\u015eAAT")
WORK = r"E:\INS AAT METRAJ PRO\autocad_connector_pycfix.py".replace("INS AAT", "\u0130N\u015eAAT")
OUT  = r"E:\INS AAT METRAJ PRO\pycfix_result.txt".replace("INS AAT", "\u0130N\u015eAAT")

# Satir ekledigimiz yer: current lines 128-154 = 27 yeni satir
# => current_line >= 155: pyc_line = current_line - 27
ADDED_START  = 128   # ilk eklenen current satir
ADDED_END    = 154   # son eklenen current satir
LINE_OFFSET  = 27    # eklenen satir sayisi

# Atlanacak sintetik instruction'lar (col_offset'leri guvenilmez)
SKIP_OPS = {'RESUME', 'COPY_FREE_VARS', 'MAKE_CELL', 'CACHE',
            'PUSH_NULL', 'POP_TOP'}  # POP_TOP bazen expr stmt col'unda

def walk_code(code_obj, line_col):
    """
    Tum code object agacini ozyinelemeli tara.
    Her (lineno, col_offset) icin MINIMUM col_offset'i kaydet.
    """
    try:
        for instr in dis.get_instructions(code_obj, show_caches=False):
            if instr.opname in SKIP_OPS:
                continue
            pos = getattr(instr, 'positions', None)
            if pos is None:
                continue
            ln  = pos.lineno
            col = pos.col_offset
            if ln is None or col is None:
                continue
            if ln not in line_col or col < line_col[ln]:
                line_col[ln] = col
    except Exception:
        pass  # bozuk code obj varsa atla

    # Nested code object'lere in
    for const in code_obj.co_consts:
        if hasattr(const, 'co_code'):
            walk_code(const, line_col)


# ── Pyc yukle ──────────────────────────────────────────────────────────────
with open(PYC, 'rb') as f:
    _magic = f.read(4)
    _flags = struct.unpack('<I', f.read(4))[0]
    _mtime = struct.unpack('<I', f.read(4))[0]
    _size  = struct.unpack('<I', f.read(4))[0]
    root_code = marshal.load(f)

# ── Pyc line -> col_offset haritasi ────────────────────────────────────────
pyc_line_col = {}
walk_code(root_code, pyc_line_col)

# ── Current source line -> col_offset cevir ────────────────────────────────
# current_line <= 127         : pyc_line = current_line  (offset=0)
# current_line 128-154        : ekledigimiz satirlar, pyc'de yok
# current_line >= 155         : pyc_line = current_line - LINE_OFFSET
current_line_col = {}
for pyc_ln, col in pyc_line_col.items():
    if pyc_ln < ADDED_START:
        cur_ln = pyc_ln                         # offset yok
    else:
        cur_ln = pyc_ln + LINE_OFFSET           # 27 satir kaydi
    # Birden fazla code obj ayni satiri claim edebilir -> minimum al
    if cur_ln not in current_line_col or col < current_line_col[cur_ln]:
        current_line_col[cur_ln] = col

# ── Kaynak oku ─────────────────────────────────────────────────────────────
with open(SRC, 'r', encoding='utf-8') as f:
    source_lines = f.readlines()

# ── Indentation uygula ──────────────────────────────────────────────────────
result = []
in_triple      = False
triple_char    = None
last_mapped_col = 0   # son eslesen col_offset (fallback icin)

for i, raw_line in enumerate(source_lines):
    lineno   = i + 1        # 1-bazli
    content  = raw_line.rstrip('\r\n')
    stripped = content.strip()

    # Bos satir — ama col_map'te varsa last_mapped_col'u guncelle
    if not stripped:
        if lineno in current_line_col:
            last_mapped_col = current_line_col[lineno]
        result.append('\n')
        continue

    # Triple-quote string ICINDE: ham cikti, bitis kontrolu
    if in_triple:
        result.append(raw_line)
        temp = stripped.replace('\\' + triple_char[0], '')
        if temp.count(triple_char) % 2 == 1:
            in_triple   = False
            triple_char = None
        continue

    # Triple-quote ACILIS kontrolu (tek satir string'i degil, tek olusum)
    for q in ('"""', "'''"):
        cnt = stripped.count(q)
        if cnt % 2 == 1:      # tek sayi => aciliyor
            in_triple   = True
            triple_char = q
            break

    # Kaynak dosyadaki gercek girinti
    src_sp = len(content) - len(content.lstrip())

    # src_sp=1 olan def/async def/@ satirlari: class body method -> col=4
    # (Closure/nested def ise col_map'te col>4 goruruz, ona guven)
    _METHOD_KWS = ('def ', 'async def ', '@')
    _is_method_line = (src_sp == 1 and
                       any(stripped.startswith(kw) for kw in _METHOD_KWS))

    # Hedef girinti belirleme
    if src_sp == 0:
        # Modul-level satir: DAIMA col=0
        target = 0
        last_mapped_col = 0
    elif _is_method_line:
        # Class body method def/decorator -> col=4
        # Istisna: closure (col_map'te col>4)
        mapped = current_line_col.get(lineno)
        if mapped is not None and mapped > 4:
            target = mapped          # nested def (closure)
        else:
            target = 4               # class body method
        last_mapped_col = target
    elif lineno in current_line_col:
        target = current_line_col[lineno]
        last_mapped_col = target   # guncelle
    else:
        # Fallback: paren-icindeki devam satirlari, type-annotated assignments,
        # comment'ler vs. -> son eslesen col seviyesini kullan.
        # Paren icinde her turlu girinti gecerli, ayni seviye kalmak mantikli.
        target = last_mapped_col

    result.append(' ' * target + stripped + '\n')

    # Blok acici satir (: ile biter, # ile baslamaz) => sonraki unmapped
    # satirlar bir seviye icerde olmali. last_mapped_col'u ilerlet.
    if stripped.endswith(':') and not stripped.startswith('#') and not in_triple:
        last_mapped_col = target + 4

# ── Post-processing: "opener olmadan indent artisi yasak" ──────────────────
# Pyc eski kod versiyonundan: bazi satirlar yanlis (cok buyuk) col alabilir.
# Kural:
#   col > prev_col AND NOT prev_was_opener  => col = prev_col  (ayni seviye kal)
#   col > prev_col AND     prev_was_opener  => col = prev_col + 4  (tam bir seviye)
# Azalmalar (dedent) ve esit seviye: dokunma.
result2     = []
prev_col2   = 0
prev_opener = False   # onceki anlamli satir ':' ile bitti mi?
in_t2       = False
tc2         = None

for line in result:
    s2       = line.rstrip('\r\n')
    strip2   = s2.strip()

    # Bos satir
    if not strip2:
        result2.append(line)
        continue

    # Triple-quote icinde: ham cikti
    if in_t2:
        result2.append(line)
        tmp = strip2.replace('\\' + tc2[0], '')
        if tmp.count(tc2) % 2 == 1:
            in_t2 = False
        continue

    for q in ('"""', "'''"):
        if strip2.count(q) % 2 == 1:
            in_t2 = True
            tc2   = q
            break

    col2 = len(s2) - len(s2.lstrip())

    if col2 > prev_col2:
        if prev_opener:
            col2 = prev_col2 + 4   # tam bir seviye artis
        else:
            col2 = prev_col2       # acici yok, koru

    result2.append(' ' * col2 + strip2 + '\n')
    prev_col2   = col2
    prev_opener = strip2.endswith(':') and not strip2.startswith('#')

# ── Yaz ────────────────────────────────────────────────────────────────────
with open(WORK, 'w', encoding='utf-8') as f:
    f.writelines(result2)

report = [
    f"Pyc line->col harita boyutu  : {len(pyc_line_col)}\n",
    f"Current line->col harita boyutu: {len(current_line_col)}\n",
    f"Haritasiz current satirlar    : "
    f"{sum(1 for i in range(1, len(source_lines)+1) if i not in current_line_col)}\n",
    f"Yazildi: {WORK}\n",
]

# ── Cleanup loop: kalan try/except hatalari icin hedefli duzeltme ───────────
# "expected 'except' or 'finally' block": bir satir try gövdesi yerine
#  try seviyesinde duruyor → onu 4 space iceri ite.
# "unexpected indent": bir satir onceki seviyeyi asıyor → onceki seviyeye indir.
# "unindent does not match": seviye eslesmeme → hata satirini onceki ile esitle.

def _get_try_idx(wlines, err_idx, err_col):
    """err_idx ustundeki en yakin try: satirini bul (ayni seviyede)."""
    for i in range(err_idx - 1, -1, -1):
        s = wlines[i].strip()
        if not s:
            continue
        c = len(wlines[i]) - len(wlines[i].lstrip())
        if c == err_col and s == 'try:':
            return i
        if c < err_col:
            break
    return None

prev_fix_line = -1
stuck = 0
MAX_CLEANUP = 100
for _ci in range(MAX_CLEANUP):
    try:
        py_compile.compile(WORK, doraise=True)
        break   # OK
    except py_compile.PyCompileError as e:
        err_str = str(e)
        m = re.search(r'line (\d+)', err_str)
        if not m:
            break
        err_line = int(m.group(1))

        # Ayni satirda sikisti mi?
        if err_line == prev_fix_line:
            stuck += 1
            if stuck >= 5:
                report.append(f"[cleanup] STUCK at L{err_line}, durdu.\n")
                break
        else:
            stuck = 0
        prev_fix_line = err_line

        with open(WORK, 'r', encoding='utf-8') as f:
            wlines = f.readlines()

        err_idx  = err_line - 1
        err_s    = wlines[err_idx]
        err_col  = len(err_s) - len(err_s.lstrip())
        err_strip = err_s.strip()

        fixed = False

        if "expected 'except'" in err_str or "expected 'finally'" in err_str:
            # Satir try: ile ayni seviyede ama except/finally degil → iceri it
            ti = _get_try_idx(wlines, err_idx, err_col)
            push_to = (err_col + 4) if ti is not None else (err_col + 4)
            wlines[err_idx] = ' ' * push_to + err_strip + '\n'
            fixed = True

        elif 'unexpected indent' in err_str:
            # Satir cok iceri → onceki anlamli satirin seviyesine indir
            prev_col = 0
            for i in range(err_idx - 1, -1, -1):
                s = wlines[i].strip()
                if s:
                    prev_col = len(wlines[i]) - len(wlines[i].lstrip())
                    break
            wlines[err_idx] = ' ' * prev_col + err_strip + '\n'
            fixed = True

        elif 'unindent does not match' in err_str:
            # Girinti bir usteki ile eslesmıyor → onceki seviyeye esitle
            prev_col = 0
            for i in range(err_idx - 1, -1, -1):
                s = wlines[i].strip()
                if s:
                    prev_col = len(wlines[i]) - len(wlines[i].lstrip())
                    break
            wlines[err_idx] = ' ' * prev_col + err_strip + '\n'
            fixed = True

        if not fixed:
            report.append(f"[cleanup] Bilinmeyen hata: {err_str[:100]}\n")
            break

        with open(WORK, 'w', encoding='utf-8') as f:
            f.writelines(wlines)
        report.append(f"[cleanup {_ci+1}] L{err_line}: {err_str.split(':')[1].strip()[:50]}\n")

# ── Final syntax dogrulama ──────────────────────────────────────────────────
try:
    py_compile.compile(WORK, doraise=True)
    report.append("SYNTAX CHECK: OK!\n")

    with open(WORK, 'r', encoding='utf-8') as f:
        wlines = f.readlines()
    levels = set()
    for l in wlines:
        sp = len(l) - len(l.lstrip(' '))
        if l.strip():
            levels.add(sp)
    report.append(f"Girinti seviyeleri: {sorted(levels)[:25]}\n")
    report.append(f"Toplam satir: {len(wlines)}\n")

    shutil.copy2(WORK, SRC)
    report.append(f"FINAL: {SRC} guncellendi.\n")

    # Pyc sil ki Python yeni kaynaktan derlesin
    import glob as _glob
    for pyc in _glob.glob(os.path.join(os.path.dirname(PYC), 'autocad_connector*.pyc')):
        os.remove(pyc)
    report.append("Eski pyc silindi - Python yeni kaynaktan derleyecek.\n")

except py_compile.PyCompileError as e:
    report.append(f"SYNTAX ERROR: {e}\n")
    err_str = str(e)
    m = re.search(r'line (\d+)', err_str)
    if m:
        err_line = int(m.group(1))
        with open(WORK, 'r', encoding='utf-8') as f:
            wlines = f.readlines()
        report.append(f"Hata L{err_line} cevresi:\n")
        for li in range(max(0, err_line - 6), min(len(wlines), err_line + 5)):
            sp = len(wlines[li]) - len(wlines[li].lstrip())
            flag = " <-- HATA" if li + 1 == err_line else ""
            report.append(f"  L{li+1:4d} sp={sp:2d}: {wlines[li].rstrip()[:90]}{flag}\n")
        # Pyc haritasinda bu bolgey goster
        report.append("\nCurrentLineCol (hata bolgesi):\n")
        for cl in range(max(1, err_line - 6), min(max(current_line_col) + 2, err_line + 5)):
            col = current_line_col.get(cl, "---")
            report.append(f"  current L{cl} -> col {col}\n")

with open(OUT, 'w', encoding='utf-8') as f:
    f.writelines(report)
print("Done")
