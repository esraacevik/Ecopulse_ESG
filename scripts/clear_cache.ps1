# Cache Temizleme Script — ESG_project
# Proje kökünden veya herhangi bir yerden çalıştırılabilir.

$ProjectRoot = Split-Path $PSScriptRoot -Parent

Write-Host "=== ECOLOGIA Cache Temizleme ===" -ForegroundColor Cyan
Write-Host "Proje: $ProjectRoot" -ForegroundColor Gray
Write-Host ""

$excludePattern = '\\node_modules\\|\\.next\\|\\.git\\|__pycache__\\'

function Should-SkipPath([string]$fullPath) {
    return $fullPath -match $excludePattern
}

# Python cache temizle
Write-Host "[1/3] Python __pycache__ klasorleri temizleniyor..." -ForegroundColor Yellow
$pycache = Get-ChildItem -Path $ProjectRoot -Recurse -Filter "__pycache__" -Directory -ErrorAction SilentlyContinue |
    Where-Object { -not (Should-SkipPath $_.FullName) }
if ($pycache) {
    $pycache | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  -> $($pycache.Count) __pycache__ klasoru temizlendi" -ForegroundColor Green
} else {
    Write-Host "  -> Cache klasoru bulunamadi" -ForegroundColor Gray
}

Write-Host "[2/3] Python bytecode dosyalari temizleniyor..." -ForegroundColor Yellow
$pyc = Get-ChildItem -Path $ProjectRoot -Recurse -Filter "*.pyc" -File -ErrorAction SilentlyContinue |
    Where-Object { -not (Should-SkipPath $_.FullName) }
$pyo = Get-ChildItem -Path $ProjectRoot -Recurse -Filter "*.pyo" -File -ErrorAction SilentlyContinue |
    Where-Object { -not (Should-SkipPath $_.FullName) }
if ($pyc) {
    $pyc | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "  -> $($pyc.Count) .pyc dosyasi temizlendi" -ForegroundColor Green
}
if ($pyo) {
    $pyo | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "  -> $($pyo.Count) .pyo dosyasi temizlendi" -ForegroundColor Green
}
if (-not $pyc -and -not $pyo) {
    Write-Host "  -> Bytecode dosyasi bulunamadi" -ForegroundColor Gray
}

# Node modules cache (opsiyonel)
Write-Host "[3/3] Node.js cache kontrol ediliyor..." -ForegroundColor Yellow
$nodeCache = Join-Path $ProjectRoot "frontend\node_modules\.cache"
if (Test-Path $nodeCache) {
    Remove-Item -Path $nodeCache -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  -> Node.js cache temizlendi" -ForegroundColor Green
} else {
    Write-Host "  -> Node.js cache bulunamadi" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== Cache temizleme tamamlandi! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Backend'i yeniden baslatmak icin:" -ForegroundColor Cyan
Write-Host "  cd $ProjectRoot\backend" -ForegroundColor White
Write-Host "  python run.py" -ForegroundColor White
