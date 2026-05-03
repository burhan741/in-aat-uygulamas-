"""
metraj_analiz_window.py dosyasindaki method body over-indent buglarini otomatik duzeltir.

Bug pattern: def metodun docstring'i 12 space ile kapaniyor (olmali 8),
ve method body'si 12+ space girintide (olmali 8).

Cozum: Her method icin docstring sonrasi ilk satirin girintisini kontrol et.
Eger >8 space ise, entire method body'yi (closing_indent - 8) space de-indent et.
"""
import re
import shutil
import os

SRC = r'e:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\metraj_analiz_window.py'
BACKUP = r'e:\İNŞAAT METRAJ PRO\metraj_analiz_window.py.bak2'
LOG = r'e:\İNŞAAT METRAJ PRO\fix_method_indent_log.txt'

# Yedek al
shutil.copy2(SRC, BACKUP)
print(f"Yedek: {BACKUP}")

with open(SRC, encoding='utf-8') as f:
    lines = f.readlines()

print(f"Toplam satir: {len(lines)}")

def get_indent(line):
    s = line.rstrip('\n')
    if not s.strip():
        return None  # Bos satir
    return len(s) - len(s.lstrip())

log_lines = []
def log(msg):
    log_lines.append(str(msg))

# Her method'u bul ve kontrol et
# Method pattern: 4 space ile baslayan "def " satirlari (class method)
new_lines = list(lines)  # kopya

fixes = []  # (start_line, end_line, deindent_amount)

i = 0
while i < len(lines):
    line = lines[i].rstrip('\n')

    # Class-level method (4 space indent)
    if re.match(r'^    def ', line):
        def_line = i
        j = i + 1

        # Docstring'i bul
        docstring_end = None
        if j < len(lines):
            stripped = lines[j].strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                q = '"""' if stripped.startswith('"""') else "'''"
                # Tek satirli docstring mi?
                rest = stripped[3:]
                if rest.endswith(q) and len(rest) >= 3:
                    docstring_end = j
                    j += 1
                else:
                    # Cok satirli - kapanisini ara
                    j += 1
                    while j < len(lines):
                        if q in lines[j]:
                            docstring_end = j
                            j += 1
                            break
                        j += 1

        # Docstring sonrasi bos satirlari atla
        body_start = j
        while body_start < len(lines) and not lines[body_start].strip():
            body_start += 1

        if body_start >= len(lines):
            i = j
            continue

        # Body'nin girdisini kontrol et
        body_indent = get_indent(lines[body_start])

        if body_indent is not None and body_indent > 8:
            excess = body_indent - 8
            log(f"BUG: def at line {def_line+1}, body at line {body_start+1} has indent={body_indent} (excess={excess})")

            # Method'un sonunu bul (bir sonraki 4-space def'e kadar)
            end = body_start + 1
            while end < len(lines):
                end_line = lines[end].rstrip('\n')
                end_indent = get_indent(end_line)
                # Bos satir ya da yorum satiri atla
                if end_indent is None:
                    end += 1
                    continue
                # Bir sonraki class-level def veya class tanimi
                if end_indent <= 4 and end_line.strip():
                    break
                end += 1

            fixes.append((body_start, end, excess, def_line + 1))
            log(f"  Fix: lines {body_start+1}-{end} deindent by {excess}")
            i = end
            continue

    i += 1

log(f"\nToplam fix: {len(fixes)}")
print(f"Toplam fix: {len(fixes)}")

# Fixleri uygula (sondan basa dogru - indeks kaymasin)
for (body_start, end, excess, def_lineno) in fixes:
    log(f"Fixing def at line {def_lineno}: lines {body_start+1}-{end}, deindent {excess}")
    for k in range(body_start, end):
        orig = new_lines[k]
        stripped = orig.rstrip('\n')
        if not stripped.strip():
            # Bos satir - olduğu gibi birak
            continue
        current_indent = len(stripped) - len(stripped.lstrip())
        if current_indent >= excess:
            new_lines[k] = ' ' * (current_indent - excess) + stripped.lstrip() + '\n'
        # else: zaten az girintili - dokunma (nadiren olur)

# Yaz
with open(SRC, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Dosya yazildi.")

# Log yaz
with open(LOG, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines))

print(f"Log: {LOG}")

# py_compile test
import py_compile
try:
    py_compile.compile(SRC, doraise=True)
    result = "py_compile: OK"
except py_compile.PyCompileError as e:
    result = f"py_compile HATA: {e}"

print(result)

# Sonucu da log'a yaz
with open(LOG, 'a', encoding='utf-8') as f:
    f.write('\n' + result + '\n')
