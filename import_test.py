import sys
import os

out = []
sys.path.insert(0, r'E:\İNŞAAT METRAJ PRO\yeni_proje')
os.chdir(r'E:\İNŞAAT METRAJ PRO\yeni_proje')

try:
    from app.ui.main_window import MainWindow
    out.append("BASARILI: MainWindow import edildi!")
    out.append(f"MainWindow: {MainWindow}")
except IndentationError as e:
    out.append(f"IndentationError: {e}")
except SyntaxError as e:
    out.append(f"SyntaxError: {e}")
except Exception as e:
    out.append(f"Diger hata ({type(e).__name__}): {e}")

with open(r'E:\İNŞAAT METRAJ PRO\import_result.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))

print('\n'.join(out))
