"""
.pyc dosyasindaki co_positions() ile her satirin orijinal sutun ofsetini al.
Bu bilgi, orijinal girin seviyesini geri olusturmak icin kullanilacak.
"""
import marshal, dis, struct

PYC = r'E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\__pycache__\main_window.cpython-311.pyc'
PY  = r'E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\main_window.py'

# .pyc yukle
with open(PYC, 'rb') as f:
    f.read(4)   # magic
    f.read(4)   # flags
    f.read(4)   # mtime
    f.read(4)   # source size
    code = marshal.load(f)

# Tum code object'lardan satir -> min_col haritasi olustur
line_min_col = {}   # line_no -> minimum col_offset
line_all_cols = {}  # line_no -> [(col, opname), ...]

def walk(c):
    try:
        positions = list(c.co_positions())
        instructions = list(dis.get_instructions(c))
        for instr, pos in zip(instructions, positions):
            if pos and pos[0] is not None:
                lineno = pos[0]
                col    = pos[2]   # col_offset (None mumkun)
                if col is not None:
                    if lineno not in line_all_cols:
                        line_all_cols[lineno] = []
                    line_all_cols[lineno].append((col, instr.opname))
                    if lineno not in line_min_col or col < line_min_col[lineno]:
                        line_min_col[lineno] = col
    except Exception as e:
        pass
    for const in c.co_consts:
        if hasattr(const, 'co_code'):
            walk(const)

walk(code)

# Kaynak satirlari oku
with open(PY, 'r', encoding='utf-8') as f:
    src_lines = f.readlines()

# Satir 42-120 arasi goster
result = []
result.append("L#   | current_indent | min_col_from_pyc | source (first 70 chars)")
result.append("-" * 90)
for lno in range(42, 121):
    src = src_lines[lno-1] if lno <= len(src_lines) else ''
    current_indent = len(src) - len(src.lstrip())
    min_col = line_min_col.get(lno, None)
    stripped = src.strip()[:70]
    marker = " <<<" if min_col is not None and min_col != current_indent else ""
    result.append(f"L{lno:4d} | cur={current_indent:3d}           | min_col={str(min_col):6}           | {stripped}{marker}")

# Istatistik: kac satirin min_col != current_indent
total = 0
mismatch = 0
for lno, src in enumerate(src_lines, 1):
    if src.strip() and lno in line_min_col:
        total += 1
        cur_ind = len(src) - len(src.lstrip())
        if line_min_col[lno] != cur_ind:
            mismatch += 1

result.append("\n" + "=" * 60)
result.append(f"Toplam satirli satir: {total}")
result.append(f"min_col != current_indent: {mismatch} (%{100*mismatch//total if total else 0})")
result.append(f"Toplam satir haritada: {len(line_min_col)}")
result.append(f"Kaynak toplam satir: {len(src_lines)}")

output = '\n'.join(result)
with open(r'E:\İNŞAAT METRAJ PRO\positions_check.txt', 'w', encoding='utf-8') as f:
    f.write(output)
print(output[:3000])
print("...Tam rapor: positions_check.txt")
