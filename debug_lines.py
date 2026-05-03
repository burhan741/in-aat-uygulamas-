"""Belirli satirlarin bytecode pozisyonlarini detayli goster"""
import marshal, dis, struct

PYC = r'E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\__pycache__\main_window.cpython-311.pyc'
PY  = r'E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\main_window.py'
START, END = 285, 300

with open(PYC, 'rb') as f:
    f.read(16)
    root_code = marshal.load(f)

# Tum instruksiyonlari topla (satir, kolon, opname, code_name)
all_instrs = []
SKIP = frozenset({'RESUME', 'COPY_FREE_VARS', 'MAKE_CELL'})

def walk(c):
    for instr in dis.get_instructions(c):
        if instr.opname in SKIP:
            continue
        pos = getattr(instr, 'positions', None)
        if pos and pos.lineno is not None and pos.col_offset is not None:
            all_instrs.append((pos.lineno, pos.col_offset, instr.opname,
                               getattr(c, 'co_name', '?'), instr.argval))
    for const in c.co_consts:
        if hasattr(const, 'co_code'):
            walk(const)

walk(root_code)

# Sadece hedef satirlari filtrele
target = [(ln, col, op, cn, av) for ln, col, op, cn, av in all_instrs
          if START <= ln <= END]

with open(PY, 'r', encoding='utf-8') as f:
    src = f.readlines()

result = []
INDENT_SIZE = 4
for lno in range(START, END+1):
    src_line = src[lno-1].rstrip() if lno <= len(src) else ''
    cur_ind = len(src_line) - len(src_line.lstrip())
    instrs = [(col, op, cn) for ln, col, op, cn, av in target if ln == lno]
    min_col = min(col for col, _, _ in instrs) if instrs else None
    rounded = (min_col // INDENT_SIZE) * INDENT_SIZE if min_col is not None else None
    stripped = src_line.strip()[:55]
    result.append(f"L{lno:4d} cur={cur_ind:2d} min_raw={str(min_col):5} rounded={str(rounded):5} | {stripped}")
    for col, op, cn in sorted(instrs)[:4]:
        result.append(f"        col={col:3d}  {op:30s} [{cn}]")

output = '\n'.join(result)
with open(r'E:\İNŞAAT METRAJ PRO\debug_result.txt', 'w', encoding='utf-8') as f:
    f.write(output)
print(output)
