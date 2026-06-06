# Start Redrob Candidate Ranker
# Launch API backend + Vue frontend

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Starting API server..." -ForegroundColor Cyan
$apiJob = Start-Job -ScriptBlock {
    Set-Location -LiteralPath $using:root
    uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
}

Start-Sleep -Seconds 3

Write-Host "Starting Vue frontend..." -ForegroundColor Cyan
$feJob = Start-Job -ScriptBlock {
    Set-Location -LiteralPath "$using:root\frontend"
    npm run dev
}

Write-Host "============================================" -ForegroundColor Green
Write-Host " Redrob Candidate Ranker" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host " API:      http://localhost:8000" -ForegroundColor Yellow
Write-Host " Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop all servers..." -ForegroundColor Gray

try {
    $apiJob | Wait-Job
} finally {
    $apiJob | Stop-Job -PassThru | Remove-Job
    $feJob | Stop-Job -PassThru | Remove-Job
    Write-Host "Servers stopped." -ForegroundColor Red
}
