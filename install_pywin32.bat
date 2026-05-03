@echo off
cd /d "E:\İNŞAAT METRAJ PRO"
echo ========================================
echo   PyWin32 Kurulum Scripti
echo ========================================
echo.

echo [1/4] Eski kurulumu kaldiriliyor...
call .venv\Scripts\pip.exe uninstall pywin32 pypiwin32 -y

echo.
echo [2/4] pywin32 yukleniyor...
call .venv\Scripts\pip.exe install pywin32

echo.
echo [3/4] Post-install script calistiriliyor...
.venv\Scripts\python.exe .venv\Scripts\pywin32_postinstall.py -install

echo.
echo [4/4] Test ediliyor...
.venv\Scripts\python.exe -c "import win32com.client; print('BASARILI: win32com.client yuklendi!')"

echo.
echo ========================================
echo   Kurulum tamamlandi!
echo ========================================
pause
