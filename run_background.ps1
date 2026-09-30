# Quantum Risk AI — Silent Background Runner with Health Probe (SIH 2026 Final)
$WorkspaceRoot = $PSScriptRoot
if (-not $WorkspaceRoot) { $WorkspaceRoot = Get-Location }

Write-Host "Starting Quantum Risk AI in the background..." -ForegroundColor Cyan

# Step 0: Stop existing processes on ports 8000 and 5173 if any
$ports = @(8000, 5173)
foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connections) {
        $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($p in $pids) {
            try { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue } catch {}
        }
    }
}
Start-Sleep -Milliseconds 500

$PythonExe = Join-Path $WorkspaceRoot "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) { $PythonExe = "python" }

# Launch Backend in Background
Start-Process powershell -WindowStyle Hidden -ArgumentList "-NoProfile", "-Command", "cd '$WorkspaceRoot\backend'; & '$PythonExe' -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

# Wait for backend health check
$retries = 0
while ($retries -lt 25) {
    Start-Sleep -Milliseconds 400
    $retries++
    try {
        $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2 -ErrorAction Stop
        if ($resp.status -eq "ok") { break }
    }
    catch {}
}

# Launch Frontend in Background
$NodePath = "C:\Users\LENOVO\AppData\Local\Programs\node-v20.12.0"
Start-Process powershell -WindowStyle Hidden -ArgumentList "-NoProfile", "-Command", "`$env:PATH = '$NodePath;' + `$env:PATH; cd '$WorkspaceRoot\frontend'; npm run dev -- --host 0.0.0.0 --port 5173"

Start-Sleep -Seconds 2

Write-Host "Services are now running in the background!" -ForegroundColor Green
Write-Host "  - Frontend:   http://127.0.0.1:5173  (or http://localhost:5173)" -ForegroundColor White
Write-Host "  - Master Demo: http://127.0.0.1:5173/sih-demo" -ForegroundColor White
Write-Host "  - Health:     http://127.0.0.1:8000/health" -ForegroundColor White
Write-Host "  - Swagger:    http://127.0.0.1:8000/docs" -ForegroundColor White
