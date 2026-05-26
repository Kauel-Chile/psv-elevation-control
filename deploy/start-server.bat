@echo off
REM Inicia el servidor de relés HW-383
REM Usar: doble click o desde terminal
cd /d "%~dp0.."
uv run uvicorn server.main:app --host 127.0.0.1 --port 8000
pause
