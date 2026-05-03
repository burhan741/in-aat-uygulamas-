"""
QuantixPro EXE Build Script
Kullanim: python build_exe.py
"""
import subprocess
import sys
import os
import shutil

VENV    = r"E:\İNŞAAT METRAJ PRO\.venv\Scripts"
PROJE   = r"E:\İNŞAAT METRAJ PRO\yeni_proje"
DIST    = r"E:\İNŞAAT METRAJ PRO\dist"
PYTHON  = os.path.join(VENV, "python.exe")
PIP     = os.path.join(VENV, "pip.exe")
PYI     = os.path.join(VENV, "pyinstaller.exe")

print("=" * 50)
print("  QuantixPro - EXE Derleme Scripti")
print("=" * 50)

# PyInstaller kontrol
r = subprocess.run([PYTHON, "-c", "import PyInstaller"], capture_output=True)
if r.returncode != 0:
    print("[!] PyInstaller bulunamadi - yukleniyor...")
    subprocess.run([PIP, "install", "pyinstaller"])

# anthropic kontrol
r = subprocess.run([PYTHON, "-c", "import anthropic"], capture_output=True)
if r.returncode != 0:
    print("[!] anthropic paketi bulunamadi - yukleniyor...")
    subprocess.run([PIP, "install", "anthropic"])

# Temizle
print("\n[1/3] Onceki derleme temizleniyor...")
for d in [os.path.join(PROJE, "dist"), os.path.join(PROJE, "build")]:
    if os.path.exists(d):
        shutil.rmtree(d)
        print(f"  Silindi: {d}")

# Pyc onceden derle
print("\n[1.5/3] Tum .py dosyalari onceden derleniyor...")
subprocess.run([PYTHON, "-m", "compileall", "-q", PROJE])

# PyInstaller
print("\n[2/3] EXE derleniyor (5-15 dakika surebilir)...")
os.chdir(PROJE)
result = subprocess.run([PYI, "InsaatMetrajPro.spec", "--noconfirm", "--clean"])

if result.returncode != 0:
    print("\n[HATA] Derleme basarisiz!")
    sys.exit(1)

# Kopyala
print("\n[3/3] Cikti kopyalaniyor...")
os.makedirs(DIST, exist_ok=True)
exe_src = os.path.join(PROJE, "dist", "QuantixPro.exe")
exe_dst = os.path.join(DIST, "QuantixPro.exe")

if os.path.exists(exe_src):
    shutil.copy2(exe_src, exe_dst)
    print("\n" + "=" * 50)
    print("  BASARILI! EXE olusturuldu:")
    print(f"  {exe_dst}")
    print("=" * 50)
    print("\nKullanicilara sadece QuantixPro.exe dosyasini verin.")
else:
    print("[HATA] QuantixPro.exe bulunamadi!")
    sys.exit(1)

input("\nDevam etmek icin Enter'a basin...")
