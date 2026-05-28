@echo off
echo Starting E-AgentScope Platform...
echo.
echo Starting Backend Server...
start "E-AgentScope Backend" cmd /k "cd /d E:\dumate\E-agentscope\backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak > nul
echo Starting Frontend Server...
start "E-AgentScope Frontend" cmd /k "cd /d E:\dumate\E-agentscope\frontend && npm run dev"
echo.
echo ========================================
echo E-AgentScope Platform Started!
echo ========================================
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:5173 (or check console)
echo ========================================
echo.
pause
