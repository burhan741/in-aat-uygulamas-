"""
Method body over-indent duzeltici - v2
"""
import re, shutil, os, py_compile, sys

# Path'i dinamik bul
script_dir = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(script_dir, 'yeni_proje', 'app', 'ui', 'metraj_analiz_window.py')
BACKUP = os.path.join(script_dir, 'maw_backup.py')
LOG = os.path.join(script_dir, 'fix_m2_log.txt')

log_lines = ['START']

def log(msg):
    log_lines.append(str(msg))
    # Her anda dosyaya yaz
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(str(msg) + '\n')
    except:
        pass

# Log dosyasini olustur
with open(LOG, 'w', encoding='utf-8') as f:
    f.write('START\n')

log(f"SRC: {SRC}")
log(f"Exists: {os.path.exists(SRC)}")

try:
    shutil.copy2(SRC, BACKUP)
    log(f"Backup OK: {BACKUP}")
except Exception as e:
    log(f"Backup error: {e}")

try:
    with open(SRC, encoding='utf-8') as f:
        lines = f.readlines()
    log(f"Read {len(lines)} lines")
except Exception as e:
    log(f"READ ERROR: {e}")
    sys.exit(1)

def get_indent(line):
    s = line.rstrip('\n')
    if not s.strip():
        return None
    return len(s) - len(s.lstrip())

new_lines = list(lines)
fixes = []

i = 0
while i < len(lines):
    line = lines[i].rstrip('\n')

    # 4 space ile baslayan def (class-level method)
    if re.match(r'^    def ', line):
        def_line = i
        j = i + 1

        # Docstring'i bul ve atla
        if j < len(lines):
            stripped_j = lines[j].strip()
            if stripped_j.startswith('"""') or stripped_j.startswith("'''"):
                q = '"""' if stripped_j.startswith('"""') else "'''"
                rest = stripped_j[3:]
                if q in rest:
                    # Tek satirli docstring
                    j += 1
                else:
                    # Cok satirli - kapanisini ara
                    j += 1
                    while j < len(lines):
                        if q in lines[j]:
                            j += 1
                            break
                        j += 1

        # Bos satirlari atla
        body_start = j
        while body_start < len(lines) and not lines[body_start].strip():
            body_start += 1

        if body_start >= len(lines):
            i = body_start
            continue

        body_indent = get_indent(lines[body_start])

        if body_indent is not None and body_indent > 8:
            excess = body_indent - 8

            # Method sonunu bul
            end = body_start + 1
            while end < len(lines):
                end_line_raw = lines[end].rstrip('\n')
                end_indent = get_indent(end_line_raw)
                if end_indent is None:
                    end += 1
                    continue
                if end_indent <= 4 and end_line_raw.strip():
                    break
                end += 1

            fixes.append((body_start, end, excess, def_line + 1))
            log(f"FIX: def L{def_line+1}, body L{body_start+1}-{end}, excess={excess}, content='{lines[body_start].strip()[:40]}'")
            i = end
            continue

    i += 1

log(f"\nToplam fix: {len(fixes)}")

# Fixleri uygula
for (body_start, end, excess, def_lineno) in fixes:
    for k in range(body_start, end):
        orig = new_lines[k]
        stripped_raw = orig.rstrip('\n')
        if not stripped_raw.strip():
            continue
        current_indent = len(stripped_raw) - len(stripped_raw.lstrip())
        new_indent = max(0, current_indent - excess)
        new_lines[k] = ' ' * new_indent + stripped_raw.lstrip() + '\n'

# Yaz
try:
    with open(SRC, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    log("Dosya yazildi OK")
except Exception as e:
    log(f"WRITE ERROR: {e}")
    sys.exit(1)

# py_compile test
try:
    py_compile.compile(SRC, doraise=True)
    log("py_compile: OK")
except py_compile.PyCompileError as e:
    log(f"py_compile HATA: {e}")

log("END")
