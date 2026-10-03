# QUANTIX PRO / İNŞAAT METRAJ PRO — PC Çökerse Geri Yükleme

Her şey iki yerde duruyor. **İkisi birlikte** programı eksiksiz geri getirir.

| Ne | Nerede | Nasıl yedekleniyor |
|---|---|---|
| Program kodu (`yeni_proje`) | GitHub `burhan741/InsaatMetrajPro` (main) | Her Claude yanıtından sonra otomatik (yedekle.ps1) |
| CLAUDE.md, PROGRAM_OZELLIKLERI.txt, yedekle.ps1, bu kılavuz | GitHub `burhan741/in-aat-uygulamas-` (master, ÖZEL) | Aynı anda otomatik |
| Veritabanları (`insaat_metraj.db` …), API anahtarı (`claude_config.json`), AutoCAD ayarları, puantaj.db, Claude hafızası | **OneDrive\QuantixPro_Yedek\veri_TARİH.zip** (son 30 sürüm) | Veri değiştiğinde otomatik zip |

> Veriler bilerek GitHub'a KONMUYOR: `InsaatMetrajPro` deposu HERKESE AÇIK — API anahtarı ve müşteri/proje verisi orada olmamalı.

## Yeni bilgisayarda adım adım

1. **Kur:** Git, Python **3.11** (Microsoft Store veya python.org), AutoCAD, OneDrive (aynı hesapla giriş yap — zip'ler kendiliğinden iner).
2. **Kodu indir** (PowerShell):
   ```powershell
   cd E:\
   git clone --recurse-submodules https://github.com/burhan741/in-aat-uygulamas-.git "İNŞAAT METRAJ PRO"
   cd "E:\İNŞAAT METRAJ PRO\yeni_proje"
   git checkout main
   ```
   `yeni_proje` klasörü boş gelirse: `git submodule update --init` (üst klasörde).
3. **Kütüphaneleri birebir aynı sürümlerle kur:**
   ```powershell
   cd "E:\İNŞAAT METRAJ PRO\yeni_proje"
   python -m pip install -r requirements-lock.txt
   ```
   (pywin32 AutoCAD bağlantısı için gerekli; listede var.)
4. **Verileri geri koy:** OneDrive\QuantixPro_Yedek içindeki EN YENİ `veri_*.zip`'i aç:
   | Zip içindeki klasör | Kopyalanacağı yer |
   |---|---|
   | `data\*` | `E:\İNŞAAT METRAJ PRO\yeni_proje\data\` |
   | `puantaj\puantaj.db` | `E:\İNŞAAT METRAJ PRO\yeni_proje\pythonanywhere\` |
   | `puantaj_backups\*` | `E:\İNŞAAT METRAJ PRO\yeni_proje\pythonanywhere\backups\` |
   | `appdata_quantix_data\*` | `%APPDATA%\QuantixPro\data\` (sadece EXE kullanıyorsan) |
   | `claude_hafiza\*` | `%USERPROFILE%\.claude\projects\E---N-AAT-METRAJ-PRO\memory\` |
   | `claude_ayar\settings.local.json` | `E:\İNŞAAT METRAJ PRO\.claude\` (otomatik yedek kancası buradan gelir) |
5. **Çalıştır:** `cd "E:\İNŞAAT METRAJ PRO\yeni_proje"; python main.py`
   EXE gerekiyorsa: üst klasörde `build_exe.bat`.
6. **Doğrula:** Program açılıyor mu, AutoCAD'e bağlanıyor mu, Asistan API anahtarını görüyor mu, eski projeler listede mi.

## Elle yedek
```powershell
powershell -ExecutionPolicy Bypass -File "E:\İNŞAAT METRAJ PRO\yedekle.ps1"
```
Son yedeklerin durumu: `E:\İNŞAAT METRAJ PRO\yedek_log.txt`.

## Yedekte OLMAYAN (yeniden kurulur, veri değil)
`.venv` (adım 3 ile kurulur), `dist/QuantixPro.exe` (build_exe.bat), `__pycache__`, programdan alınan Excel çıktıları (Masaüstü vb. — isterseniz OneDrive'a kaydedin).
