@echo off
echo.
echo ============================================
echo   ECU Master Lab - Deploiement Railway
echo ============================================
echo.

cd /d "%~dp0"

powershell -ExecutionPolicy Bypass -File deploy-railway.ps1

pause
