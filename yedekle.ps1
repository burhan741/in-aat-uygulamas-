# ============================================================================
#  QUANTIX PRO / INSAAT METRAJ PRO - TAM YEDEK (Rev-167)
#  Claude Code "Stop" kancasi her yanittan sonra bunu calistirir; elle de calisir:
#      powershell -ExecutionPolicy Bypass -File "E:\INSAAT METRAJ PRO\yedekle.ps1"
#
#  1) yeni_proje (program kodu)  -> git commit + push  (GitHub: InsaatMetrajPro, main)
#  2) ust klasor (CLAUDE.md vb.) -> git commit + push  (GitHub: in-aat-uygulamas-, master)
#  3) VERILER (git'e GIRMEZ: veritabani, API anahtari, ayarlar, puantaj, Claude hafizasi)
#     -> OneDrive\QuantixPro_Yedek\veri_YYYY-MM-DD_HHmm.zip  (sadece degisiklik varsa,
#        son 30 zip tutulur). OneDrive buluta esitler -> PC cokse de veri durur.
#  Hata olursa yedek_log.txt'ye yazar; hicbir adim digerini durdurmaz.
# ============================================================================
$ErrorActionPreference = "Continue"
$KOK = $PSScriptRoot
$KOD = Join-Path $KOK "yeni_proje"
$LOG = Join-Path $KOK "yedek_log.txt"
$ZAMAN = Get-Date -Format "yyyy-MM-dd HH:mm"

function Log($m) {
    $satir = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $m"
    Add-Content -Path $LOG -Value $satir -Encoding UTF8
}

function GitYedek($klasor, $dal, $ad) {
    try {
        Push-Location $klasor
        git add -A 2>$null | Out-Null
        git diff --staged --quiet 2>$null
        if ($LASTEXITCODE -ne 0) {
            git commit -q -m "auto-backup: $ZAMAN" 2>$null | Out-Null
            Log "$ad : commit atildi"
        }
        $ileride = git rev-list --count "origin/$dal..$dal" 2>$null
        if ($ileride -and [int]$ileride -gt 0) {
            git push -q origin $dal 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) { Log "$ad : $ileride commit GitHub'a gonderildi" }
            else { Log "$ad : PUSH BASARISIZ (internet / GitHub girisi?) - commit yerelde duruyor" }
        }
    } catch {
        Log "$ad : HATA $($_.Exception.Message)"
    } finally {
        Pop-Location
    }
}

# 1) Program kodu ONCE (ust klasor alt modul isaretcisini dogru commit'e baglasin)
GitYedek $KOD "main" "yeni_proje"
# 2) Ust klasor
GitYedek $KOK "master" "ust_klasor"

# 3) Veriler -> OneDrive
try {
    $od = $env:OneDrive
    if (-not $od) { $od = Join-Path $env:USERPROFILE "OneDrive" }
    if (-not (Test-Path $od)) { Log "VERI: OneDrive bulunamadi - veri yedegi ALINMADI"; exit 0 }
    $hedef = Join-Path $od "QuantixPro_Yedek"
    New-Item -ItemType Directory -Force -Path $hedef | Out-Null

    $kaynaklar = @(
        @{ Yol = (Join-Path $KOD "data");                       Ad = "data" },
        @{ Yol = (Join-Path $KOD "pythonanywhere\puantaj.db");  Ad = "puantaj" },
        @{ Yol = (Join-Path $KOD "pythonanywhere\backups");     Ad = "puantaj_backups" },
        @{ Yol = (Join-Path $env:APPDATA "QuantixPro\data");    Ad = "appdata_quantix_data" },
        @{ Yol = (Join-Path $env:USERPROFILE ".claude\projects\E---N-AAT-METRAJ-PRO\memory"); Ad = "claude_hafiza" },
        @{ Yol = (Join-Path $KOK ".claude\settings.local.json"); Ad = "claude_ayar" }
    )
    $gecici = Join-Path $env:TEMP ("quantix_yedek_" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Force -Path $gecici | Out-Null
    foreach ($k in $kaynaklar) {
        if (Test-Path $k.Yol) {
            $hedefAlt = Join-Path $gecici $k.Ad
            if ((Get-Item $k.Yol).PSIsContainer) {
                New-Item -ItemType Directory -Force -Path $hedefAlt | Out-Null
                Copy-Item -Path (Join-Path $k.Yol "*") -Destination $hedefAlt -Recurse -Force -ErrorAction SilentlyContinue
            } else {
                New-Item -ItemType Directory -Force -Path $hedefAlt | Out-Null
                Copy-Item -Path $k.Yol -Destination $hedefAlt -Force -ErrorAction SilentlyContinue
            }
        }
    }
    # Degisiklik yoksa yeni zip uretme (her yanitta 10 MB birikmesin)
    $ozet = (Get-ChildItem $gecici -Recurse -File | Sort-Object FullName |
             ForEach-Object { (Get-FileHash $_.FullName -Algorithm SHA1).Hash + $_.FullName.Substring($gecici.Length) }) -join "|"
    $ozetHash = [BitConverter]::ToString(
        [Security.Cryptography.SHA1]::Create().ComputeHash([Text.Encoding]::UTF8.GetBytes($ozet))).Replace("-", "")
    $sonHashDosya = Join-Path $hedef "son_yedek_hash.txt"
    $sonHash = if (Test-Path $sonHashDosya) { (Get-Content $sonHashDosya -Raw).Trim() } else { "" }
    if ($ozetHash -ne $sonHash) {
        $zip = Join-Path $hedef ("veri_" + (Get-Date -Format "yyyy-MM-dd_HHmm") + ".zip")
        Compress-Archive -Path (Join-Path $gecici "*") -DestinationPath $zip -Force
        Set-Content -Path $sonHashDosya -Value $ozetHash -Encoding ASCII
        Log "VERI: $zip olusturuldu ($([math]::Round((Get-Item $zip).Length / 1MB, 2)) MB)"
        Get-ChildItem $hedef -Filter "veri_*.zip" | Sort-Object Name -Descending | Select-Object -Skip 30 |
            Remove-Item -Force -ErrorAction SilentlyContinue
    }
    Remove-Item -Recurse -Force $gecici -ErrorAction SilentlyContinue
} catch {
    Log "VERI: HATA $($_.Exception.Message)"
}
exit 0
