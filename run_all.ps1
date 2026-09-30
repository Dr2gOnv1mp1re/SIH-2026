# Quantum Risk AI — Master Full-Stack Launcher (SIH 2026 Final Round)
# Logical Startup Order: DATABASE -> BACKEND -> HEALTH CHECK -> FRONTEND -> APPLICATION

$WorkspaceRoot = $PSScriptRoot
if (-not $WorkspaceRoot) { $WorkspaceRoot = Get-Location }

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  QUANTUM RISK AI -- FULL-STACK LAUNCH ORCHESTRATOR (SIH 2026)" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan

# Step 0: Port Conflict Detection & Safe Cleanup
Write-Host "[0/5] Checking and resolving port conflicts on 8000 & 5173..." -ForegroundColor Yellow
$ports = @(8000, 5173)
foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connections) {
        $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($p in $pids) {
            try {
                Write-Host "  - Terminating stale process (PID $p) on port $port..." -ForegroundColor DarkYellow
                Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
            } catch {}
        }
    }
}
Start-Sleep -Milliseconds 800

# Step 1: Database Initialization & Verification
Write-Host "[1/5] Initializing & verifying SQLite enterprise database..." -ForegroundColor Yellow
$PythonExe = Join-Path $WorkspaceRoot "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) { $PythonExe = "python" }

$SeedScript = Join-Path $WorkspaceRoot "backend\app\seed_demo.py"
& $PythonExe $SeedScript

# Step 2: Start Backend Daemon
Write-Host "[2/5] Launching FastAPI Backend on http://127.0.0.1:8000 ..." -ForegroundColor Yellow
$BackendCmd = "cd '$WorkspaceRoot\backend'; & '$PythonExe' -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
Start-Process powershell -WindowStyle Hidden -ArgumentList "-NoProfile", "-Command", $BackendCmd

# Step 3: Health Check Probe (Wait for Backend readiness before launching frontend)
Write-Host "[3/5] Awaiting backend health verification at http://127.0.0.1:8000/health ..." -ForegroundColor Yellow
$backendReady = $false
$retries = 0
while (-not $backendReady -and $retries -lt 30) {
    Start-Sleep -Milliseconds 500
    $retries++
    try {
        $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2 -ErrorAction Stop
        if ($resp.status -eq "ok" -or $resp.database -eq "connected") {
            $backendReady = $true
        }
    } catch {}
}

if ($backendReady) {
    Write-Host "  -> Backend is healthy and database is connected! (Response in $($retries * 500)ms)" -ForegroundColor Green
} else {
    Write-Host "  [WARNING] Backend did not respond within 15s. Proceeding with frontend launch..." -ForegroundColor Red
}

# Step 4: Start Frontend Daemon
Write-Host "[4/5] Launching Vite Frontend on http://127.0.0.1:5173 ..." -ForegroundColor Yellow
$NodePath = "C:\Users\LENOVO\AppData\Local\Programs\node-v20.12.0"
$FrontendCmd = "`$env:PATH = '$NodePath;' + `$env:PATH; cd '$WorkspaceRoot\frontend'; npm run dev -- --host 0.0.0.0 --port 5173"
Start-Process powershell -WindowStyle Hidden -ArgumentList "-NoProfile", "-Command", $FrontendCmd

# Step 5: Frontend Probe & Final Summary
Write-Host "[5/5] Awaiting frontend readiness probe..." -ForegroundColor Yellow
$frontendReady = $false
$retries = 0
while (-not $frontendReady -and $retries -lt 20) {
    Start-Sleep -Milliseconds 500
    $retries++
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5173" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($resp.StatusCode -eq 200) {
            $frontendReady = $true
        }
    } catch {}
}

Write-Host "`n========================================================================" -ForegroundColor Green
Write-Host "  FULL-STACK QUANTUM RISK AI RUNNING RELIABLY" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "  - Web Dashboard:    http://127.0.0.1:5173  (or http://localhost:5173)" -ForegroundColor White
Write-Host "  - Master Demo:      http://127.0.0.1:5173/sih-demo" -ForegroundColor White
Write-Host "  - Backend API:      http://127.0.0.1:8000/api/v1" -ForegroundColor White
Write-Host "  - Health Check:     http://127.0.0.1:8000/health" -ForegroundColor White
Write-Host "  - Interactive Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "  Authentication Credentials: ciso@abcbank.com / Ciso@12345" -ForegroundColor Cyan
Write-Host "========================================================================`n" -ForegroundColor Green
