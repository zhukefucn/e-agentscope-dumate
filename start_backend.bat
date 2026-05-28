@echo off
echo Starting E-AgentScope Backend...
cd /d E:\dumate\E-agentscope\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
