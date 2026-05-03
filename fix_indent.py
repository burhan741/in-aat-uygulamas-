"""
Simple py_compile checker for metraj_analiz_window.py.
Writes error location and context to LOG.
"""
import py_compile
import re

SRC = r"E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\metraj_analiz_window.py"
LOG = r"E:\İNŞAAT METRAJ PRO\fix_indent_log.txt"

log_lines = []
def log(msg):
    log_lines.append(str(msg))
    print(msg)

def get_indent(line):
    s = line.lstrip(' ')
    if not s.strip():
        return 999
    return len(line) - len(s)

import datetime
log(f"Run at: {datetime.datetime.now()}")

with open(SRC, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

log(f"Read {len(lines)} lines")

try:
    py_compile.compile(SRC, doraise=True)
    log("py_compile: OK")
except py_compile.PyCompileError as e:
    err_str = str(e)
    log(f"ERROR: {err_str}")
    m = re.search(r'line (\d+)', err_str)
    if m:
        el = int(m.group(1))
        log(f"Context around line {el}:")
        for ln in range(max(0, el-10), min(len(lines), el+6)):
            log(f"  {ln+1:5d} ({get_indent(lines[ln]):3d}): {repr(lines[ln].rstrip()[:100])}")

with open(LOG, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines))
print("Log written to:", LOG)
print("Log ->", LOG)
