import ezdxf
import re

doc = ezdxf.readfile('D:/Drawing1.dxf')
msp = doc.modelspace()

output = []
output.append('=== LAYER LİSTESİ ===')
layers = {}
for e in msp:
    layer = e.dxf.layer
    etype = e.dxftype()
    if layer not in layers:
        layers[layer] = {'count': 0, 'types': set()}
    layers[layer]['count'] += 1
    layers[layer]['types'].add(etype)

for layer, info in sorted(layers.items()):
    output.append(f'{layer}: {info["count"]} nesne - {info["types"]}')

output.append('')
output.append('=== LWPOLYLINE LAYERLARI ===')
poly_layers = set()
for e in msp.query('LWPOLYLINE'):
    poly_layers.add(e.dxf.layer)
output.append(f'Polyline bulunan layerlar: {poly_layers}')

output.append('')
output.append('=== TEXT/MTEXT ÖRNEKLERİ ===')
REGEX_DEMIR = r"(?:P\d+\s+)?(\d+)\s*[ØøΦφ/Nn]?\s*(\d+)\s*L\s*=\s*(\d+)"
count = 0
demir_count = 0
demir_ornekleri = []
for e in msp.query('TEXT MTEXT'):
    txt = e.dxf.text if e.dxftype() == 'TEXT' else e.text
    txt_clean = txt.upper().replace("\n", " ").strip()
    layer = e.dxf.layer

    match = re.search(REGEX_DEMIR, txt_clean)
    if match:
        demir_count += 1
        demir_ornekleri.append(f'[DEMİR] [{layer}] {txt_clean[:100]}')
    elif count < 30:
        output.append(f'[{layer}] {txt_clean[:100]}')
        count += 1

output.append('')
output.append('=== BULUNAN DEMİR YAZILARI ===')
for d in demir_ornekleri[:20]:
    output.append(d)

output.append('')
output.append('=== ÖZET ===')
output.append(f'Toplam demir yazısı bulundu: {demir_count}')
output.append(f'H_KAT layer var mı: {"H_KAT" in layers}')
output.append(f'H_KIRIS layer var mı: {"H_KIRIS" in layers}')
output.append(f'A_KAT_ISMI layer var mı: {"A_KAT_ISMI" in layers}')

# Dosyaya yaz
with open('E:/İNŞAAT METRAJ PRO/analiz_sonuc.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print('Analiz tamamlandı: E:/İNŞAAT METRAJ PRO/analiz_sonuc.txt')
