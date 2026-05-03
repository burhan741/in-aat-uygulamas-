# QuantixPro — EXE Derleme Scripti (PowerShell)
# Calistirma: PowerShell'de build_exe.ps1'e cift tikla VEYA
#   Set-ExecutionPolicy Bypass -Scope Process; .\build_exe.ps1

$ErrorActionPreference = "Stop"

# PSScriptRoot = bu .ps1 dosyasinin bulundugu klasor (hardcoded path yok)
$ProjeKok = $PSScriptRoot
$Proje    = Join-Path $ProjeKok "yeni_proje"
$Venv     = Join-Path $ProjeKok ".venv\Scripts"
$Python   = Join-Path $Venv "python.exe"
$Pip      = Join-Path $Venv "pip.exe"
$PyInst   = Join-Path $Venv "pyinstaller.exe"
$Dist     = Join-Path $ProjeKok "dist"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  QuantixPro EXE Derleme Basliyor..." -ForegroundColor Cyan
Write-Host "  Proje: $ProjeKok" -ForegroundColor Gray
Write-Host "============================================"
Write-Host ""

# --- PyInstaller kurulu mu? ---
Write-Host "[Kontrol] PyInstaller..." -NoNewline
$piOk = & $Python -c "import PyInstaller; print('ok')" 2>$null
if ($piOk -eq "ok") {
    Write-Host " KURULU" -ForegroundColor Green
} else {
    Write-Host " BULUNAMADI, yukleniyor..." -ForegroundColor Yellow
    & $Pip install pyinstaller --quiet
}

# --- anthropic kurulu mu? ---
Write-Host "[Kontrol] anthropic..." -NoNewline
$antOk = & $Python -c "import anthropic; print('ok')" 2>$null
if ($antOk -eq "ok") {
    Write-Host " KURULU" -ForegroundColor Green
} else {
    Write-Host " BULUNAMADI, yukleniyor..." -ForegroundColor Yellow
    & $Pip install anthropic --quiet
}

# --- Eski build temizle ---
Write-Host ""
Write-Host "[1/3] Onceki derleme temizleniyor..."
Remove-Item -Recurse -Force (Join-Path $Proje "dist")  -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force (Join-Path $Proje "build") -ErrorAction SilentlyContinue
Write-Host "      Temizlendi." -ForegroundColor Green

# --- EXE derle ---
Write-Host ""
Write-Host "[2/3] EXE derleniyor (5-15 dakika surebilir)..." -ForegroundColor Yellow
Set-Location $Proje

$proc = Start-Process -FilePath $PyInst `
    -ArgumentList "InsaatMetrajPro.spec", "--noconfirm", "--clean" `
    -NoNewWindow -Wait -PassThru

if ($proc.ExitCode -ne 0) {
    Write-Host ""
    Write-Host "[HATA] Derleme basarisiz! (ExitCode=$($proc.ExitCode))" -ForegroundColor Red
    Read-Host "Devam icin Enter"
    exit 1
}

# --- Kopyala ---
Write-Host ""
Write-Host "[3/3] EXE kopyalaniyor..."
if (-not (Test-Path $Dist)) { New-Item -ItemType Directory -Path $Dist | Out-Null }

$ExeSrc = Join-Path $Proje "dist\QuantixPro.exe"
$ExeDst = Join-Path $Dist "QuantixPro.exe"

if (Test-Path $ExeSrc) {
    Copy-Item $ExeSrc $ExeDst -Force
    $boyutMB = [math]::Round((Get-Item $ExeDst).Length / 1MB, 1)
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "  BASARILI!" -ForegroundColor Green
    Write-Host "  $ExeDst" -ForegroundColor White
    Write-Host "  Boyut: $boyutMB MB" -ForegroundColor White
    Write-Host "============================================" -ForegroundColor Green
} else {
    Write-Host "[HATA] QuantixPro.exe bulunamadi!" -ForegroundColor Red
}

Write-Host ""
Read-Host "Tamamlandi. Enter ile cik"
