"""
Duzeltilmis versiyon: instr.positions direkt kullanimi (zip yerine)
Python 3.11'de co_positions() ve get_instructions() CACHE nedeniyle
hizalama kaybi yasanir. instr.positions daha dogrudur.
"""
import marshal, dis, struct

PYC = r'E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\__pycache__\main_window.cpython-311.pyc'
PY  = r'E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\main_window.py'

with open(PYC, 'rb') as f:
    f.read(16)
    code = marshal.load(f)

# Tum code object'lardan satir -> min_col olustur (instr.positions ile)
line_min_col = {}

def walk(c):
    for instr in dis.get_instructions(c):
        pos = getattr(instr, 'positions', None)
        if pos and pos.lineno is not None and pos.col_offset is not None:
            ln  = pos.lineno
            col = pos.col_offset
            if ln not in line_min_col or col < line_min_col[ln]:
                line_min_col[ln] = col
    for const in c.co_consts:
        if hasattr(const, 'co_code'):
            walk(const)

walk(code)

with open(PY, 'r', encoding='utf-8') as f:
    src_lines = f.readlines()

# Istatistik
total_code_lines = sum(1 for l in src_lines if l.strip() and not l.strip().startswith('#'))
covered = sum(1 for i, l in enumerate(src_lines, 1)
              if l.strip() and not l.strip().startswith('#') and i in line_min_col)

result = []
result.append(f"Toplam kod satiri (yorum haric): {total_code_lines}")
result.append(f"Kapsanan satir (min_col var): {covered} (%{100*covered//total_code_lines})")
result.append(f"Haritadaki toplam satir: {len(line_min_col)}")
result.append("")

# Satir 42-120 ornegi
result.append("L#   | mevcut_indent | pyc_min_col | kaynak")
result.append("-" * 80)
for lno in range(42, 121):
    src = src_lines[lno-1] if lno <= len(src_lines) else ''
    cur_ind = len(src) - len(src.lstrip())
    min_col = line_min_col.get(lno, None)
    stripped = src.strip()[:60]
    marker = " <<<" if min_col is not None and min_col != cur_ind else ""
    result.append(f"L{lno:4d} | {str(cur_ind):13} | {str(min_col):11} | {stripped}{marker}")

output = '\n'.join(result)
with open(r'E:\İNŞAAT METRAJ PRO\positions_check2.txt', 'w', encoding='utf-8') as f:
    f.write(output)
print(output[:3000])
