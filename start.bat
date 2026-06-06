@echo off
cd /d "%~dp0"

echo Starting API server...
start "Redrob API" cmd /c "uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo Starting Vue frontend...
cd frontend
start "Redrob Frontend" cmd /c "npm run dev"

echo.
echo ============================================
echo  Redrob Candidate Ranker
echo ============================================
echo  API:        http://localhost:8000
echo  Frontend:   http://localhost:3000
echo ============================================
echo.
echo Press any key to stop all servers...
pause >nul

taskkill /f /fi "windowtitle eq Redrob API" >nul 2>&1
taskkill /f /fi "windowtitle eq Redrob Frontend" >nul 2>&1
echo Servers stopped.
