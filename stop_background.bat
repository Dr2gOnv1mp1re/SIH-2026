@echo off
title Quantum Risk AI — Stop Background Services
powershell -Command "$ports = @(8000, 5173); foreach ($port in $ports) { $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue; if ($connections) { $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique; foreach ($p in $pids) { try { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue; Write-Host ('Stopped process on port ' + $port) } catch {} } } }"
echo Stopped Quantum Risk AI background processes on ports 8000 and 5173.
pause
