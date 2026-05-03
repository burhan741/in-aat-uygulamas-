"""
surdurulebilirlik_window.py girinti düzeltme
Satır 29-659: method body'ler 1 boşluk yerine 2 boşluk olmalı.
`def ` satırları (method tanımları) olduğu gibi kalır.
"""
filepath = r"E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\surdurulebilirlik_window.py"

with open(filepath, 'rb') as f:
    content = f.read()

sep = b'\r\n' if b'\r\n' in content else b'\n'
lines = content.split(sep)

FIX_START = 29   # __init__ body başlangıcı (1-indexed)
FIX_END   = 659  # _get_button_style sonu

new_lines = []
for i, line in enumerate(lines):
    lineno = i + 1  # 1-indexed

    if FIX_START <= lineno <= FIX_END:
        stripped = line.lstrip(b' \t')
        if line.strip() == b'':
            # Boş satır — olduğu gibi
            new_lines.append(line)
        elif stripped.startswith(b'def '):
            # Method tanımı — 1 boşlukta kalmalı
            new_lines.append(line)
        else:
            # Method body satırı — 1 boşluk ekle (1->2)
            new_lines.append(b' ' + line)
    else:
        new_lines.append(line)

new_content = sep.join(new_lines)

with open(filepath, 'wb') as f:
    f.write(new_content)

print(f"Toplam satır: {len(lines)}")
print(f"Düzeltme aralığı: {FIX_START}-{FIX_END}")
print("Tamamlandı.")
