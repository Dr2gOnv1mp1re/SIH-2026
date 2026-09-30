@echo off
title Quantum Risk AI — Silent Background Starter
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "%~dp0run_background.ps1"
pause
