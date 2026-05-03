@echo off
chcp 65001 >nul
cd /d "E:\İNŞAAT METRAJ PRO"

echo ========================================
echo   PyWin32 Kurulumu
echo ========================================
echo.

.venv\Scripts\python.exe -m pip install pywin32

echo.
echo Test ediliyor...
.venv\Scripts\python.exe -c "import win32com.client; print('BASARILI: pywin32 calisiyor!')"

echo.
pause
