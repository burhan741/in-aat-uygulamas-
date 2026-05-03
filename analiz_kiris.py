import ezdxf
import re

doc = ezdxf.readfile('D:/Drawing1.dxf')
msp = doc.modelspace()

# T, K, TK, MK ile başlayan kiriş isimlerini ara
REGEX_KIRIS = r"\b[TKM]+\d+\b"

output = []
output.append("=== KİRİŞ/TEMEL İSİMLERİ ARAMA ===")
output.append("")

kiris_isimleri = {}
for e in msp.query('TEXT MTEXT'):
    txt = e.dxf.text if e.dxftype() == 'TEXT' else e.text
    txt_clean = txt.upper().replace("\n", " ").strip()
    layer = e.dxf.layer

    # T19, K1, TK5, MK3 gibi isimleri ara
    matches = re.findall(REGEX_KIRIS, txt_clean)
    for m in matches:
        if m not in kiris_isimleri:
            kiris_isimleri[m] = {'layer': layer, 'count': 0, 'ornek': txt_clean}
        kiris_isimleri[m]['count'] += 1

output.append(f"Bulunan kiriş/temel isimleri: {len(kiris_isimleri)}")
output.append("")

for isim, info in sorted(kiris_isimleri.items()):
    output.append(f"{isim}: Layer={info['layer']}, Tekrar={info['count']}, Örnek={info['ornek'][:50]}")

output.append("")
output.append("=== TÜM LAYER'LARDA T/K İÇEREN YAZILAR ===")

count = 0
for e in msp.query('TEXT MTEXT'):
    txt = e.dxf.text if e.dxftype() == 'TEXT' else e.text
    txt_clean = txt.upper().replace("\n", " ").strip()
    layer = e.dxf.layer

    # T veya K ile başlayan ve sayı içeren
    if re.search(r"\bT\d+", txt_clean) or re.search(r"\bK\d+", txt_clean):
        output.append(f"[{layer}] {txt_clean[:80]}")
        count += 1
        if count > 50:
            break

with open('E:/kiris_analiz.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("Analiz tamamlandi: E:/kiris_analiz.txt")
