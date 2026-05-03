"""Run autopep8 on broken autocad_connector.py and test result."""
import subprocess, shutil, os, py_compile

SRC   = r"E:\INS AAT METRAJ PRO\yeni_proje\app\core\autocad_connector.py".replace("INS AAT", "\u0130N\u015eAAT")
FIXED = r"E:\INS AAT METRAJ PRO\autocad_connector_autopep8.py".replace("INS AAT", "\u0130N\u015eAAT")
OUT   = r"E:\INS AAT METRAJ PRO\autopep8_result.txt".replace("INS AAT", "\u0130N\u015eAAT")
VENV  = r"E:\INS AAT METRAJ PRO\.venv\Scripts\python.exe".replace("INS AAT", "\u0130N\u015eAAT")

# Copy source
shutil.copy2(SRC, FIXED)

results = []
results.append(f"Kaynak kopyalandi: {FIXED}\n")

# Run autopep8 with aggressive mode
r = subprocess.run(
    [VENV, "-m", "autopep8",
     "--aggressive", "--aggressive",
     "--select=E1,W1",
     "--max-line-length=200",
     "--in-place", FIXED],
    capture_output=True, text=True, timeout=120
)
results.append(f"autopep8 exit code: {r.returncode}\n")
results.append(f"stdout: {r.stdout[:500]}\n")
results.append(f"stderr: {r.stderr[:500]}\n")

# Test py_compile
try:
    py_compile.compile(FIXED, doraise=True)
    results.append("SYNTAX CHECK: OK - BASARILI!\n")
except py_compile.PyCompileError as e:
    results.append(f"SYNTAX ERROR (hala hata var): {e}\n")
    # Show error context
    import re as re_mod
    m = re_mod.search(r'line (\d+)', str(e))
    if m:
        err_line = int(m.group(1))
        with open(FIXED, 'r', encoding='utf-8') as f:
            flines = f.readlines()
        results.append(f"Hata cevresindeki satirlar:\n")
        for li in range(max(0, err_line-3), min(len(flines), err_line+3)):
            sp = len(flines[li]) - len(flines[li].lstrip())
            results.append(f"  L{li+1:4d} sp={sp}: {flines[li].rstrip()[:80]}\n")

# Check unique indent levels in fixed file
with open(FIXED, 'r', encoding='utf-8') as f:
    flines = f.readlines()

indent_levels = set()
for line in flines:
    s = line.lstrip(' ')
    if s.strip():
        sp = len(line) - len(s)
        if sp > 0:
            indent_levels.add(sp)

results.append(f"\nDuzeltilmis dosya girinti seviyeleri: {sorted(indent_levels)[:30]}\n")
results.append(f"Toplam satir: {len(flines)}\n")

with open(OUT, 'w', encoding='utf-8') as f:
    f.writelines(results)
print("Done")
