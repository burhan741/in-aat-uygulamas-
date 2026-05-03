"""
Bu script metraj_analiz_window.py dosyasında indentation buglarini bulur.
Pattern: if ...: return  ardından fazla girintili kod
"""
import re

SRC = r'e:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\metraj_analiz_window.py'
LOG = r'e:\İNŞAAT METRAJ PRO\indent_bugs.txt'

with open(SRC, encoding='utf-8') as f:
    lines = f.readlines()

bugs = []

# Pattern 1: Docstring sonrası yanlış indent (""" ile kapanan docstring'den sonra)
# Method body 8 space olmalı ama 12 veya daha fazla ise bug
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.rstrip('\n')
    indent = len(stripped) - len(stripped.lstrip())

    # def ile başlayan metodlar
    if re.match(r'    def ', stripped):
        # Metodun beklenen body indent'i = 8
        expected = 8
        j = i + 1
        # Docstring atla
        if j < len(lines) and lines[j].strip().startswith('"""'):
            # Çok satırlı docstring
            if lines[j].strip() == '"""' or (lines[j].strip().count('"""') == 1 and not lines[j].strip().endswith('"""')):
                j += 1
                while j < len(lines) and '"""' not in lines[j]:
                    j += 1
                j += 1  # """ kapatan satırı atla
            else:
                j += 1  # tek satır docstring

        # Docstring sonrası ilk gerçek satırı kontrol et
        while j < len(lines) and not lines[j].strip():
            j += 1

        if j < len(lines):
            first_body = lines[j].rstrip('\n')
            body_indent = len(first_body) - len(first_body.lstrip())
            if body_indent > expected + 0 and first_body.strip():
                bugs.append({
                    'line': j + 1,
                    'def_line': i + 1,
                    'expected': expected,
                    'got': body_indent,
                    'content': first_body.strip()[:60]
                })

    i += 1

# Pattern 2: Orphan except/else at wrong level
for i, line in enumerate(lines):
    stripped = line.rstrip('\n')
    s = stripped.strip()
    indent = len(stripped) - len(stripped.lstrip())

    if s.startswith('except ') and indent <= 4 and indent > 0:
        bugs.append({
            'line': i + 1,
            'type': 'orphan_except',
            'indent': indent,
            'content': s[:60]
        })

with open(LOG, 'w', encoding='utf-8') as f:
    f.write(f"Toplam bulgu: {len(bugs)}\n\n")
    for bug in bugs[:50]:  # ilk 50
        f.write(str(bug) + '\n')

print(f"Bulgu sayisi: {len(bugs)}")
print(f"Log: {LOG}")
