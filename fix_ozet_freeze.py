"""
Proje Özeti sekmesi donma düzeltmesi:
tight_layout() -> subplots_adjust() ile değiştir (çok daha hızlı)
"""
path = r"E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\main_window.py"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

original = content

# Donut chart tight_layout -> subplots_adjust (legend sağda olduğu için right=0.72)
content = content.replace(
    'self.kategori_figure.tight_layout(pad=1.0)',
    'self.kategori_figure.subplots_adjust(left=0.05, right=0.72, top=0.90, bottom=0.05)'
)

# Bar chart tight_layout -> subplots_adjust
content = content.replace(
    'self.pahali_figure.tight_layout(pad=1.2)',
    'self.pahali_figure.subplots_adjust(left=0.30, right=0.95, top=0.90, bottom=0.15)'
)

if content == original:
    print("HATA: Değişiklik yapılamadı, pattern bulunamadı!")
    # Debug
    if 'tight_layout' in content:
        import re
        for m in re.finditer(r'tight_layout[^\n]*', content):
            print(f"  Bulunan: {repr(m.group())}")
    else:
        print("  tight_layout hiç yok dosyada")
else:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    n = original.count('tight_layout') - content.count('tight_layout')
    print(f"OK: {n} adet tight_layout -> subplots_adjust ile değiştirildi")
