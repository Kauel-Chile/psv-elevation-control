@echo off
REM Inicia el servidor de relés HW-383
REM Usar: doble click o desde terminal

cd /d "%~dp0.."

REM python -m server lee .env automaticamente y usa SelectorEventLoop en Windows
uv run python -m server
pause
