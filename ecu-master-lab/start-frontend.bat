@echo off
echo ===================================
echo   ECU Master Lab - Frontend
echo ===================================
cd /d "%~dp0frontend"
echo.
echo Installation des dépendances...
npm install
echo.
echo Démarrage du serveur Next.js...
echo Frontend disponible sur: http://localhost:3000
echo.
npm run dev
pause
