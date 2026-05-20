# Veri dosyalarini dogrular; eski kok hardlink'lerini temizler.
# GitHub klonundan sonra: powershell -ExecutionPolicy Bypass -File scripts/setup_data.ps1

$ProjectRoot = Split-Path $PSScriptRoot -Parent
$DataDir = Join-Path $ProjectRoot "data"

Write-Host "=== Ecopulse_ESG Veri Kurulumu ===" -ForegroundColor Cyan
Write-Host ""

$required = @("scope1_data.json", "scope2_data.json", "summary.json")
$optional = @("emission_data_input.json", "scope3_data.json")
$ok = $true

foreach ($file in $required) {
    $path = Join-Path $DataDir $file
    if (Test-Path $path) {
        Write-Host "[OK] data/$file" -ForegroundColor Green
    } else {
        Write-Host "[EKSIK] data/$file" -ForegroundColor Red
        $ok = $false
    }
}

foreach ($file in $optional) {
    $path = Join-Path $DataDir $file
    if (Test-Path $path) {
        Write-Host "[OK] data/$file (opsiyonel)" -ForegroundColor Green
    } else {
        Write-Host "[BILGI] data/$file yok (opsiyonel)" -ForegroundColor Gray
    }
}

# Eski kok / streamlit hardlink veya kopyalarini kaldir (artik data/ kullaniliyor)
$stalePaths = @(
    (Join-Path $ProjectRoot "scope1_data.json"),
    (Join-Path $ProjectRoot "scope2_data.json"),
    (Join-Path $ProjectRoot "summary.json"),
    (Join-Path $ProjectRoot "emission_data_input.json"),
    (Join-Path $ProjectRoot "streamlit\scope1_data.json"),
    (Join-Path $ProjectRoot "streamlit\scope2_data.json"),
    (Join-Path $ProjectRoot "streamlit\summary.json"),
    (Join-Path $ProjectRoot "streamlit\emission_data_input.json")
)

Write-Host ""
Write-Host "Kok/streamlit eski JSON baglantilari temizleniyor..." -ForegroundColor Yellow
foreach ($p in $stalePaths) {
    if (Test-Path $p) {
        Remove-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue
        Write-Host "  Silindi: $p" -ForegroundColor Gray
    }
}

Write-Host ""
if ($ok) {
    Write-Host "Veri kurulumu tamam. Tum JSON dosyalari data/ klasorunde." -ForegroundColor Green
} else {
    Write-Host "Eksik zorunlu dosyalar var. data/ klasorunu kontrol edin." -ForegroundColor Red
    exit 1
}
