@echo off
echo ===================================
echo   ECU MASTER LAB v1.0
echo   Plateforme SaaS ECU + Agent IA
echo   PostgreSQL + FastAPI + Next.js
echo ===================================
echo.
echo [1/4] Démarrage de PostgreSQL (Docker)...
docker-compose up -d
timeout /t 5 /nobreak >nul
echo.
echo [2/4] Installation des dépendances Backend...
cd /d "%~dp0backend"
pip install -r requirements.txt
echo.
echo [3/4] Démarrage du Backend (FastAPI)...
start "ECU Master Lab - Backend" cmd /c "cd /d %~dp0backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002"
timeout /t 5 /nobreak >nul
echo.
echo [4/4] Démarrage du Frontend (Next.js)...
start "ECU Master Lab - Frontend" cmd /c "cd /d %~dp0frontend && npm install && npm run dev"
echo.
echo ===================================
echo   Services demarres:
echo   PostgreSQL: localhost:5432
echo   Backend:    http://localhost:8002
echo   Frontend:   http://localhost:3000
echo   API Docs:   http://localhost:8002/docs
echo ===================================
echo.
pause
