path = r"E:\İNŞAAT METRAJ PRO\yeni_proje\app\ui\main_window.py"
with open(path, 'rb') as f:
    content = f.read()

lines = content.split(b'\n')

# Aranacak fonksiyon isimlerini bul - satırın BAŞINDAN itibaren
targets = [b'calculate_materials', b'create_malzeme_tab', b'export_materials_supplier']
for t in targets:
    for i, l in enumerate(lines):
        if b'def ' in l and t in l:
            leading = len(l) - len(l.lstrip(b' \t'))
            first_bytes = [hex(b) for b in l[:leading]]
            print(f"Line {i+1:5d}: indent={leading} chars={first_bytes} | {l[:55]}")
            break

print("\n=== Fonksiyon body indent tespiti (create_malzeme_tab) ===")
found = False
for i, l in enumerate(lines):
    if b'def create_malzeme_tab' in l:
        found = True
        for j in range(0, 5):
            ll = lines[i+j]
            leading = len(ll) - len(ll.lstrip(b' \t'))
            chars = [hex(b) for b in ll[:leading]]
            print(f"  Line {i+j+1}: indent={leading} chars={chars} | {ll[:50]}")
        break
