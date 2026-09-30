@echo off
title Quantum Risk AI — Master Orchestrator (SIH 2026)
cd /d "%~dp0"
echo ========================================================================
echo   QUANTUM RISK AI -- FULL-STACK LAUNCH ORCHESTRATOR (SIH 2026)
echo ========================================================================

powershell -ExecutionPolicy Bypass -File "%~dp0run_all.ps1"
pause
