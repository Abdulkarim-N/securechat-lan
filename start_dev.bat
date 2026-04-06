@echo off
echo Starting SecureChat LAN Development Environment...

:: Instance 1 Backend
start "Backend 1 (port 8000)" cmd /k "cd /d %~dp0 && venv\Scripts\activate && cd backend && uvicorn main:app --port 8000 --reload"

:: Wait for backend 1 to start
timeout /t 3 /nobreak

:: Instance 2 Backend
start "Backend 2 (port 8001)" cmd /k "cd /d %~dp0 && venv\Scripts\activate && cd backend && uvicorn main:app --port 8001 --reload"

:: Wait for backend 2 to start
timeout /t 3 /nobreak

:: Instance 1 Frontend
start "Frontend 1 (port 5173)" cmd /k "cd /d %~dp0frontend && npm run dev"

:: Instance 2 Frontend
start "Frontend 2 (port 5174)" cmd /k "cd /d %~dp0frontend && npm run dev -- --port 5174 --mode instance2"

echo.
echo All 4 terminals launched!
echo.
echo Instance 1: http://localhost:5173  (Backend: http://127.0.0.1:8000)
echo Instance 2: http://localhost:5174  (Backend: http://127.0.0.1:8001)
pause