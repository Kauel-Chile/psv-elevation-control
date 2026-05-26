#!/usr/bin/env bash
# Instala el servicio systemd para que el server arranque al iniciar sesión.
#
# Requisitos:
#   1. Estar en el grupo uucp (para acceder al serial sin sudo):
#      sudo usermod -aG uucp $USER
#      Cerrar sesión y volver a entrar.
#
#   2. Tener las dependencias instaladas:
#      cd /home/vitto/PSV/PROYECTOS/psv-elevation-control
#      uv sync
#
# Uso:
#   bash deploy/install-service.sh
#
# Después de instalar:
#   systemctl --user start psv-relay-server   # iniciar ahora
#   systemctl --user status psv-relay-server  # ver estado
#   journalctl --user -u psv-relay-server -f  # ver logs en tiempo real

set -euo pipefail

SERVICE="psv-relay-server.service"
SRC="deploy/$SERVICE"
DST="$HOME/.config/systemd/user/$SERVICE"

if [ ! -f "$SRC" ]; then
	echo "❌ No se encuentra $SRC"
	echo "   Ejecutá este script desde la raíz del proyecto."
	exit 1
fi

mkdir -p "$HOME/.config/systemd/user"
cp "$SRC" "$DST"

systemctl --user daemon-reload
systemctl --user enable "$SERVICE"

echo "✅ Servicio instalado."
echo ""
echo "Para iniciar ahora:"
echo "  systemctl --user start $SERVICE"
echo ""
echo "Para ver logs:"
echo "  journalctl --user -u $SERVICE -f"
echo ""
echo "⚠️  No olvides agregarte al grupo uucp si no lo hiciste:"
echo "  sudo usermod -aG uucp $USER"
echo "  (cerrar sesión y volver a entrar)"
