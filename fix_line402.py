"""Line 402'deki fazla boşlukları temizle, else: için doğru indent uygula"""
filepath = r"E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\main_window.py"

with open(filepath, 'rb') as f:
    content = f.read()
sep = b'\r\n' if b'\r\n' in content else b'\n'
lines = list(content.split(sep))

# Line 402 (1-indexed) = index 401
idx = 401
line = lines[idx]
stripped = line.strip()
print(f"Line 402 current indent: {len(line) - len(line.lstrip())} spaces")
print(f"Line 402 content: {stripped!r}")

# Doğru indent: 4 boşluk (if hasattr satırı 4 boşlukta)
lines[idx] = b'    ' + stripped

# Ayrıca "unexpected indent" tipi IndentationError'ları da kontrol et
# ve fazla boşluklu satırları düzelt (1000+ spaces)
for i, line in enumerate(lines):
    stripped_l = line.strip()
    if not stripped_l:
        continue
    indent = len(line) - len(line.lstrip())
    if indent > 50:  # Anormal derecede fazla boşluk
        print(f"  Line {i+1}: {indent} spaces - content: {stripped_l[:50]!r}")

with open(filepath, 'wb') as f:
    f.write(sep.join(lines))
print("Kaydedildi.")
