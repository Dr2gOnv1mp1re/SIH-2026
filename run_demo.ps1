# ==============================================================================
# QUANTUM RISK AI - Master Automated Demonstration Launcher (SIH 2026)
# ==============================================================================

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  QUANTUM RISK AI: Cyber Risk Quantification & Investment Optimizer   " -ForegroundColor Yellow
Write-Host "  Smart India Hackathon (SIH) Master Demonstration Environment        " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$BackendDir = "d:\SIH\backend"
$FrontendDir = "d:\SIH\frontend"
$NodePath = "C:\Users\LENOVO\AppData\Local\Programs\node-v20.12.0"
$PythonExe = "$BackendDir\.venv\Scripts\python.exe"

$env:PYTHONPATH = "$BackendDir;$env:PYTHONPATH"

# 1. Run Automated Test Suite Verification
Write-Host "[1/3] Running Backend Verification Tests (Pytest)..." -ForegroundColor Cyan
& "$BackendDir\.venv\Scripts\pytest.exe" "$BackendDir\tests" -q --disable-warnings
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Some tests reported issues, but proceeding with live server launch..." -ForegroundColor Yellow
} else {
    Write-Host "Backend Test Suite: 100% PASSED (Risk, Financial, OR-Tools, Blockchain verified)." -ForegroundColor Green
}
Write-Host ""

# 2. Launch FastAPI Backend on Port 8000
Write-Host "[2/3] Launching FastAPI Backend Server on http://localhost:8000..." -ForegroundColor Cyan
$BackendProcess = Start-Process -FilePath $PythonExe -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" -WorkingDirectory $BackendDir -PassThru
Write-Host "FastAPI Server Running [PID: $($BackendProcess.Id)]" -ForegroundColor Green
Write-Host "API Interactive Docs: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""

# 3. Launch Vite React Frontend on Port 5173
Write-Host "[3/3] Launching Vite React Cyberpunk Dashboard on http://localhost:5173..." -ForegroundColor Cyan
$env:Path = "$NodePath;$env:Path"
$FrontendProcess = Start-Process -FilePath "$NodePath\npm.cmd" -ArgumentList "run", "dev" -WorkingDirectory $FrontendDir -PassThru
Write-Host "Frontend Dashboard Running [PID: $($FrontendProcess.Id)]" -ForegroundColor Green
Write-Host ""

Write-Host "======================================================================" -ForegroundColor Green
Write-Host "  PLATFORM IS LIVE AND READY FOR EVALUATION!                          " -ForegroundColor Yellow
Write-Host "  - Open Dashboard:     http://localhost:5173                         " -ForegroundColor Cyan
Write-Host "  - Open Swagger Docs:  http://localhost:8000/docs                    " -ForegroundColor Cyan
Write-Host "  - Demo Controller:    Step through 18 SIH steps in top header bar   " -ForegroundColor Magenta
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "Press Ctrl+C or close this window to stop both servers." -ForegroundColor Gray

# Keep script alive
try {
    while ($true) {
        Start-Sleep -Seconds 2
    }
} finally {
    Write-Host "Stopping servers..." -ForegroundColor Yellow
    Stop-Process -Id $BackendProcess.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $FrontendProcess.Id -Force -ErrorAction SilentlyContinue
    Write-Host "Demonstration environment stopped." -ForegroundColor Red
}
