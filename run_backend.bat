@echo off
title Quantum Risk AI — FastAPI Backend Engine
cd /d "%~dp0\backend"
echo ========================================================================
echo   Starting Quantum Risk AI Backend (FastAPI on http://localhost:8000)
echo ========================================================================
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
) else (
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
)
pause
