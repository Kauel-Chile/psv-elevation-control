@echo off
REM Inicia el servidor de relés HW-383
REM Usar: doble click o desde terminal

cd /d "%~dp0.."

REM Cargar variables de .env si existe
if exist .env (
    for /f "usebackq tokens=1,2 delims==" %%a in (.env) do (
        if "%%a"=="RELAY_PORT" set RELAY_PORT=%%b
        if "%%a"=="RELAY_HOST" set RELAY_HOST=%%b
    )
)

if "%RELAY_PORT%"=="" set RELAY_PORT=8000
if "%RELAY_HOST%"=="" set RELAY_HOST=127.0.0.1

uv run uvicorn server.main:app --host %RELAY_HOST% --port %RELAY_PORT%
pause
