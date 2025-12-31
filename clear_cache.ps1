# Cache Temizleme Script
Write-Host "=== ECOLOGIA Cache Temizleme ===" -ForegroundColor Cyan
Write-Host ""

# Python cache temizle
Write-Host "[1/3] Python __pycache__ klasorleri temizleniyor..." -ForegroundColor Yellow
$pycache = Get-ChildItem -Path "ecologia" -Recurse -Filter "__pycache__" -Directory -ErrorAction SilentlyContinue
if ($pycache) {
    $pycache | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  -> $($pycache.Count) __pycache__ klasoru temizlendi" -ForegroundColor Green
} else {
    Write-Host "  -> Cache klasoru bulunamadi" -ForegroundColor Gray
}

Write-Host "[2/3] Python bytecode dosyalari temizleniyor..." -ForegroundColor Yellow
$pyc = Get-ChildItem -Path "ecologia" -Recurse -Filter "*.pyc" -File -ErrorAction SilentlyContinue
$pyo = Get-ChildItem -Path "ecologia" -Recurse -Filter "*.pyo" -File -ErrorAction SilentlyContinue
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
$nodeModules = Get-ChildItem -Path "ecologia/frontend" -Filter "node_modules/.cache" -Directory -ErrorAction SilentlyContinue
if ($nodeModules) {
    $nodeModules | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  -> Node.js cache temizlendi" -ForegroundColor Green
} else {
    Write-Host "  -> Node.js cache bulunamadi" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== Cache temizleme tamamlandi! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Backend'i yeniden baslatmak icin:" -ForegroundColor Cyan
Write-Host "  cd ecologia/backend" -ForegroundColor White
Write-Host "  python run.py" -ForegroundColor White

