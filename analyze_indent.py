"""
autocad_connector.py indentation structure analyzer.
Pyc-guided approach: code object depths map source lines to nesting levels.
"""
import dis, importlib.util, importlib.machinery, types, struct, os

src  = r"E:\İNŞAAT METRAJ PRO\yeni_proje\app\core\autocad_connector.py"
pyc  = r"E:\İNŞAAT METRAJ PRO\yeni_proje\app\core\__pycache__\autocad_connector.cpython-311.pyc"
out  = r"E:\İNŞAAT METRAJ PRO\analyze_result.txt"

lines_report = []

# ── Load pyc ──────────────────────────────────────────────────────────────────
loader = importlib.machinery.SourcelessFileLoader("_ac", pyc)
spec   = importlib.util.spec_from_loader("_ac", loader)
mod    = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
module_code = spec.loader.get_code("_ac")

# ── Walk all nested code objects ──────────────────────────────────────────────
def walk_code(code_obj, depth=0):
    yield code_obj, depth
    for const in code_obj.co_consts:
        if isinstance(const, types.CodeType):
            yield from walk_code(const, depth + 1)

# ── Build line → min_depth map ─────────────────────────────────────────────────
line_depth = {}
code_owners = {}  # line → code_obj.co_name

for code_obj, depth in walk_code(module_code):
    try:
        # Python 3.10+ : co_lines() yields (start_offset, end_offset, lineno)
        for _, _, lineno in code_obj.co_lines():
            if lineno is not None:
                if lineno not in line_depth or line_depth[lineno] > depth:
                    line_depth[lineno] = depth
                    code_owners[lineno] = code_obj.co_name
    except AttributeError:
        # Fallback: use dis.get_instructions
        for instr in dis.get_instructions(code_obj):
            ln = instr.positions.lineno if hasattr(instr, 'positions') and instr.positions else None
            if ln and (ln not in line_depth or line_depth[ln] > depth):
                line_depth[ln] = depth
                code_owners[ln] = code_obj.co_name

lines_report.append(f"Toplam pyc line bilgisi: {len(line_depth)} satir\n")
lines_report.append(f"Depth dagilimi: {sorted(set(line_depth.values()))}\n\n")

# ── Show sample lines at each depth ───────────────────────────────────────────
with open(src, 'r', encoding='utf-8') as f:
    src_lines = f.readlines()

for depth_val in sorted(set(line_depth.values())):
    sample_lines = [(ln, src_lines[ln-1].rstrip(), code_owners.get(ln,'?'))
                    for ln, d in line_depth.items() if d == depth_val]
    sample_lines.sort()
    lines_report.append(f"=== DEPTH {depth_val} ({len(sample_lines)} satir) ===\n")
    for ln, content, owner in sample_lines[:8]:
        sp = len(content) - len(content.lstrip())
        lines_report.append(f"  L{ln:4d} sp={sp} [{owner}]: {content[:70]}\n")
    if len(sample_lines) > 8:
        lines_report.append(f"  ... ve {len(sample_lines)-8} satir daha\n")
    lines_report.append("\n")

# ── Show actual 2-space lines ─────────────────────────────────────────────────
lines_report.append("=== 2-SPACE SATIRLAR (ilk 20) ===\n")
cnt = 0
for i, line in enumerate(src_lines):
    sp = len(line) - len(line.lstrip(' '))
    if sp == 2:
        lines_report.append(f"  L{i+1:4d}: {line.rstrip()[:80]}\n")
        cnt += 1
        if cnt >= 20:
            break

with open(out, 'w', encoding='utf-8') as f:
    f.writelines(lines_report)
print("Done")
