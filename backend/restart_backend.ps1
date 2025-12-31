# Backend Restart Script
Write-Host "Backend yeniden baslatiliyor..." -ForegroundColor Green

# Mevcut uvicorn process'lerini durdur
Get-Process | Where-Object {$_.ProcessName -eq "uvicorn" -or ($_.ProcessName -eq "python" -and $_.CommandLine -like "*uvicorn*")} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Cache temizle
Write-Host "Python cache temizleniyor..." -ForegroundColor Yellow
Get-ChildItem -Path ".." -Recurse -Filter "__pycache__" -Directory -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path ".." -Recurse -Filter "*.pyc" -File -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path ".." -Recurse -Filter "*.pyo" -File -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host "Cache temizlendi!" -ForegroundColor Green
Write-Host "Backend baslatiliyor..." -ForegroundColor Yellow

# Backend'i başlat
python run.py

