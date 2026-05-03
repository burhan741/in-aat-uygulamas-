@echo off
chcp 65001 >nul
cd /d "E:\İNŞAAT METRAJ PRO"

echo ========================================
echo   VENV ONARIM SCRIPTI
echo ========================================
echo.

echo [1/5] Mevcut Python surumunu kontrol ediliyor...
where python
python --version

echo.
echo [2/5] Eski .venv siliniyor...
if exist ".venv" (
    rmdir /s /q ".venv"
    echo    Eski .venv silindi.
) else (
    echo    .venv bulunamadi.
)

echo.
echo [3/5] Yeni virtual environment olusturuluyor...
python -m venv .venv

echo.
echo [4/5] pip guncelleniyor ve pywin32 yukleniyor...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install pywin32

echo.
echo [5/5] Test ediliyor...
.venv\Scripts\python.exe -c "import win32com.client; print('BASARILI: win32com.client calisiyor!')"

echo.
echo ========================================
echo   TAMAMLANDI!
echo ========================================
echo.
echo Simdi projenin diger bagimliklarini yukleyin:
echo   .venv\Scripts\pip install PyQt6 ezdxf pandas openpyxl matplotlib shapely
echo.
pause
