"""return satirlari icin bytecode analizi"""
import marshal, dis

PYC = r'E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\__pycache__\main_window.cpython-311.pyc'
PY  = r'E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\main_window.py'
OUT = r'E:\İNŞAAT METRAJ PRO\debug_ret_result.txt'

SKIP = frozenset({'RESUME', 'COPY_FREE_VARS', 'MAKE_CELL'})
ANON = frozenset({'<lambda>', '<listcomp>', '<dictcomp>', '<setcomp>', '<genexpr>'})
# return satirlari - hem sabit tuple hem degisken ornekleri
TARGET = {3971, 3976, 3978, 3929, 3930, 3965}

with open(PYC, 'rb') as f:
    f.read(16)
    root_code = marshal.load(f)

all_instrs = []

def walk(c):
    cname = getattr(c, 'co_name', '?')
    is_anon = cname in ANON
    for instr in dis.get_instructions(c):
        if instr.opname in SKIP:
            continue
        pos = getattr(instr, 'positions', None)
        if pos and pos.lineno is not None and pos.col_offset is not None:
            if pos.lineno in TARGET:
                if is_anon and pos.col_offset == 0:
                    continue
                all_instrs.append((pos.lineno, pos.col_offset, instr.opname, cname))
    for const in c.co_consts:
        if hasattr(const, 'co_code'):
            walk(const)

walk(root_code)

with open(PY, 'r', encoding='utf-8') as f:
    src = f.readlines()

lines = ["=== RETURN SATIRLARI DEBUG ===", ""]
for lno in sorted(TARGET):
    line_instrs = [(col, op, cn) for (ln, col, op, cn) in all_instrs if ln == lno]
    src_line = src[lno-1].rstrip() if lno <= len(src) else ''
    stripped = src_line.strip()[:70]
    if line_instrs:
        min_col = min(col for col, _, _ in line_instrs)
        rounded = (min_col // 4) * 4
        lines.append(f"L{lno}: min_col={min_col} -> rounded={rounded} | {stripped}")
        for col, op, cn in sorted(line_instrs, key=lambda x: x[0]):
            lines.append(f"       col={col:3d}  {op:30s} [{cn}]")
    else:
        lines.append(f"L{lno}: NO INSTRUCTIONS | {stripped}")
    lines.append("")

result = '\n'.join(lines)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(result)
print(result)
