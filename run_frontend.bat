@echo off
title Quantum Risk AI — Vite Frontend Dashboard
cd /d "%~dp0\frontend"
echo ========================================================================
echo   Starting Quantum Risk AI Frontend (Vite on http://localhost:5173)
echo ========================================================================
set "PATH=C:\Users\LENOVO\AppData\Local\Programs\node-v20.12.0;%PATH%"
npm run dev
pause
