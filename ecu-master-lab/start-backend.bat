@echo off
echo ===================================
echo   ECU Master Lab - Backend
echo   PostgreSQL + FastAPI
echo ===================================
cd /d "%~dp0backend"
echo.
echo [1/2] PostgreSQL via Docker...
docker-compose up -d
timeout /t 3 /nobreak >nul
echo.
echo [2/2] Demarrage du serveur FastAPI...
echo API: http://localhost:8002
echo Docs: http://localhost:8002/docs
echo DB: PostgreSQL localhost:5432
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
pause
