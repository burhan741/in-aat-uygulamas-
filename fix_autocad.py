"""
autocad_connector.py kalici indentation duzeltici.

Strateji:
1. Pyc'deki instruction positions (col_offset) orijinal dogru girintiyi verir.
2. Satirlari original kaynak satirina map'leyip dogru col_offset'i uygulariz.
3. Pyc verisi olmayan satirlar (biz ekledik veya yorum/bos) komsu satirdan alinir.
4. Sonucu py_compile ile dogrulariz.
"""
import dis, importlib.util, importlib.machinery, types

SRC  = r"E:\INS AAT METRAJ PRO\yeni_proje\app\core\autocad_connector.py".replace("INS AAT", "\u0130N\u015eAAT")
PYC  = r"E:\INS AAT METRAJ PRO\yeni_proje\app\core\__pycache__\autocad_connector.cpython-311.pyc".replace("INS AAT", "\u0130N\u015eAAT")
OUT  = r"E:\INS AAT METRAJ PRO\fix_result.txt".replace("INS AAT", "\u0130N\u015eAAT")

report = []

# ── Load pyc ──────────────────────────────────────────────────────────────────
loader = importlib.machinery.SourcelessFileLoader("_ac", PYC)
spec   = importlib.util.spec_from_loader("_ac", loader)
spec.loader.exec_module(importlib.util.module_from_spec(spec))
module_code = spec.loader.get_code("_ac")

# ── Walk code objects ─────────────────────────────────────────────────────────
def walk_code(code_obj):
    yield code_obj
    for c in code_obj.co_consts:
        if isinstance(c, types.CodeType):
            yield from walk_code(c)

# ── Build lineno → min_col_offset from pyc positions ─────────────────────────
# col_offset = doğru girinti (orijinal kaynaktan derlendi)
line_col = {}   # original_lineno -> correct_col_offset

for co in walk_code(module_code):
    try:
        instrs = list(dis.get_instructions(co, show_caches=False))
    except TypeError:
        instrs = list(dis.get_instructions(co))

    for instr in instrs:
        pos = getattr(instr, 'positions', None)
        if pos is None:
            continue
        ln = getattr(pos, 'lineno', None)
        co_off = getattr(pos, 'col_offset', None)
        if ln is not None and co_off is not None:
            # En küçük col_offset = satırın başlangıç girintisi
            if ln not in line_col or line_col[ln] > co_off:
                line_col[ln] = co_off

report.append(f"Pyc'den cekilen satir/col_offset ciftleri: {len(line_col)}\n")
sample = sorted(line_col.items())[:20]
report.append(f"Ornek (ilk 20): {sample}\n\n")

# ── Read current source ───────────────────────────────────────────────────────
with open(SRC, 'r', encoding='utf-8') as f:
    src_lines = f.readlines()

# Bizim eklemelerimiz: satir 128-154 (0-indexed: 127-153) — 27 yeni satir
INSERT_START = 128   # 1-based, bu satir DAHIL yeni
INSERT_END   = 154   # 1-based, bu satir DAHIL yeni
N_INSERTED   = INSERT_END - INSERT_START + 1   # = 27

def original_lineno(current_1based):
    """current source 1-based satir → pyc'deki original satir no."""
    if current_1based < INSERT_START:
        return current_1based
    elif current_1based <= INSERT_END:
        return None   # bizim ekleme, pyc'de yok
    else:
        return current_1based - N_INSERTED

# ── Rebuild with correct indentation ─────────────────────────────────────────
fixed_lines = []
last_known_col = 0   # pyc'den gelmeyen satirlar icin fallback

for i, line in enumerate(src_lines):
    current_1 = i + 1
    stripped  = line.rstrip('\r\n')
    content   = stripped.lstrip(' ')
    n_spaces  = len(stripped) - len(content)

    # Bos veya sadece bosluk
    if not content:
        fixed_lines.append('\n')
        continue

    orig = original_lineno(current_1)
    correct_col = line_col.get(orig) if orig is not None else None

    if correct_col is None:
        # Yorum, devam satirı, ya da bizim yeni eklememiz:
        # Mevcut girintiye gore fallback — zaten module-level ya da ayni block
        # Modül-level yeni satirlar (128-154) zaten 0 ya da 1 space kullanıyor,
        # bu dogru, dokundurma.
        fixed_lines.append(line)
        continue

    # col_offset ≥ 0 → bu kadar space koy, sonra icerik
    new_line = ' ' * correct_col + content + '\n'
    fixed_lines.append(new_line)
    last_known_col = correct_col

# ── Write fixed file ──────────────────────────────────────────────────────────
FIXED = SRC.replace('.py', '_FIXED.py')
with open(FIXED, 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

report.append(f"Duzeltilmis dosya yazildi: {FIXED}\n")

# ── Verify with py_compile ────────────────────────────────────────────────────
import py_compile
try:
    py_compile.compile(FIXED, doraise=True)
    report.append("SYNTAX CHECK: OK\n")
except py_compile.PyCompileError as e:
    report.append(f"SYNTAX ERROR: {e}\n")
    # Find the error line
    err_str = str(e)
    import re as re_mod
    m = re_mod.search(r'line (\d+)', err_str)
    if m:
        err_line = int(m.group(1))
        report.append(f"Hata satiri {err_line} icerigi:\n")
        with open(FIXED, 'r', encoding='utf-8') as f:
            flines = f.readlines()
        for li in range(max(0, err_line-3), min(len(flines), err_line+2)):
            report.append(f"  L{li+1:4d}: {flines[li].rstrip()[:80]}\n")

with open(OUT, 'w', encoding='utf-8') as f:
    f.writelines(report)
print("Done")
