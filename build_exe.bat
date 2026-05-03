@echo off
chcp 65001 > nul
echo ============================================
echo   QuantixPro - EXE Derleme Scripti
echo   Her guncelleme sonrasi bu scripti calistir
echo ============================================
echo.

set "VENV=E:\İNŞAAT METRAJ PRO\.venv\Scripts"
set "PROJE=E:\İNŞAAT METRAJ PRO\yeni_proje"
set "DIST=E:\İNŞAAT METRAJ PRO\dist"

echo VENV: %VENV%
echo PROJE: %PROJE%

:: PyInstaller kurulu mu kontrol et
"%VENV%\python.exe" -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo [!] PyInstaller bulunamadi - yukleniyor...
    "%VENV%\pip.exe" install pyinstaller
)

:: anthropic kurulu mu kontrol et
"%VENV%\python.exe" -c "import anthropic" 2>nul
if %errorlevel% neq 0 (
    echo [!] anthropic paketi bulunamadi - yukleniyor...
    "%VENV%\pip.exe" install anthropic
)

echo.
echo [1/3] Onceki derleme temizleniyor...
if exist "%PROJE%\dist" rmdir /s /q "%PROJE%\dist"
if exist "%PROJE%\build" rmdir /s /q "%PROJE%\build"

echo.
echo [1.5/3] Tum .py dosyalari onceden derleniyor (pyc cache)...
"%VENV%\python.exe" -m compileall -q "%PROJE%"

echo.
echo [2/3] EXE derleniyor (5-15 dakika surebilir)...
cd /d "%PROJE%"
"%VENV%\pyinstaller.exe" InsaatMetrajPro.spec --noconfirm --clean

if %errorlevel% neq 0 (
    echo.
    echo [HATA] Derleme basarisiz! Hata mesajini kontrol edin.
    pause
    exit /b 1
)

echo.
echo [3/3] Cikti kopyalaniyor...
if not exist "%DIST%" mkdir "%DIST%"
if exist "%PROJE%\dist\QuantixPro.exe" (
    copy /y "%PROJE%\dist\QuantixPro.exe" "%DIST%\QuantixPro.exe"
    echo.
    echo ============================================
    echo   BASARILI! EXE olusturuldu:
    echo   %DIST%\QuantixPro.exe
    echo ============================================
    echo.
    echo Kullanicilara sadece QuantixPro.exe dosyasini verin.
    echo Ilk acilista veriler AppData\QuantixPro\ altina kopyalanir.
) else (
    echo [HATA] QuantixPro.exe bulunamadi!
)

pause
