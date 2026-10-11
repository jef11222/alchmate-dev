@echo off
title Local System Security Scanner
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Scan-Security.ps1"
echo.
pause
