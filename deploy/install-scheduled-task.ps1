<#
.SYNOPSIS
    Instala el servidor de relés como tarea programada al iniciar sesión.
.DESCRIPTION
    Crea una tarea en el Programador de Tareas de Windows que inicia
    el servidor automáticamente al iniciar sesión, sin ventana visible.
    Se reinicia automáticamente si falla.

    Ejecutar como usuario normal (no admin) — funciona en el inicio
    de sesión del usuario actual.
#>

$TaskName = "PSV-Relay-Server"

# Obtiene la ruta absoluta del script actual y sube dos niveles
$ScriptPath = $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent (Split-Path -Parent $ScriptPath)

# Verificar que uv existe
$UvPath = Get-Command "uv" -ErrorAction SilentlyContinue
if (-not $UvPath) {
    Write-Host "❌ uv no encontrado. Instalá uv: https://docs.astral.sh/uv/" -ForegroundColor Red
    exit 1
}

# Verificar que el proyecto tiene el server
if (-not (Test-Path "$ProjectDir/server/main.py")) {
    Write-Host "❌ No se encuentra server/main.py en $ProjectDir" -ForegroundColor Red
    Write-Host "   Ejecutá este script desde la carpeta deploy/ del proyecto." -ForegroundColor Red
    exit 1
}

# Ruta completa a uv
$UvExe = (Get-Command "uv").Source

Write-Host "📦 Proyecto:    $ProjectDir" -ForegroundColor Cyan
Write-Host "📦 uv:          $UvExe" -ForegroundColor Cyan

# Eliminar tarea existente si hay
schtasks /query /tn $TaskName 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    schtasks /delete /tn $TaskName /f | Out-Null
    Write-Host "🗑️  Tarea anterior eliminada." -ForegroundColor Yellow
}

# Cargar config desde .env (si existe)
$EnvFile = "$ProjectDir\.env"
$Port = 8000
$Host = "127.0.0.1"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^RELAY_PORT=(\d+)$') { $Port = [int]$Matches[1] }
        if ($_ -match '^RELAY_HOST=(.+)$')   { $Host  = $Matches[1] }
    }
}

# Crear tarea programada (inicia al iniciar sesión, sin ventana)
$Action = New-ScheduledTaskAction `
    -Execute "$UvExe" `
    -Argument "run uvicorn server.main:app --host $Host --port $Port" `
    -WorkingDirectory "$ProjectDir"

$Trigger = New-ScheduledTaskTrigger -AtLogOn

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable

$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType S4U `
    -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Force | Out-Null

Write-Host ""
Write-Host "✅ Tarea '$TaskName' instalada." -ForegroundColor Green
Write-Host ""
Write-Host "Para iniciar ahora mismo:" -ForegroundColor Cyan
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
Write-Host ""
Write-Host "Para ver logs:" -ForegroundColor Cyan
Write-Host "  Get-ScheduledTask -TaskName '$TaskName' | Get-ScheduledTaskInfo" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  El usuario necesita permiso de escritura en el puerto COM." -ForegroundColor Yellow
Write-Host "   Conectar el NodeMCU antes de iniciar sesión." -ForegroundColor Yellow
