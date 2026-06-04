# PSV Elevation Control

Control de relés HW-383 con **SparkFun ESP32 Thing** + MicroPython.

## Requisitos

- **ESP32** (SparkFun Thing u otra placa ESP32 con MicroPython)
- Módulo de relés HW-383 (2 canales)
- Cable USB con datos
- `esptool` y `mpremote` instalados:
  ```bash
  uv tool install esptool
  uv tool install mpremote
  ```

## Instalación de MicroPython en ESP32

### 1. Descargar firmware

Última versión estable para ESP32 desde [micropython.org](https://micropython.org/download/ESP32_GENERIC/).

O directamente:
```bash
curl -LO https://micropython.org/resources/firmware/ESP32_GENERIC-20240602-v1.23.0.bin
```

### 2. Poner ESP32 en modo flash

1. Mantener presionado **BOOT**
2. Presionar **RST** (sin soltar BOOT)
3. Soltar **RST**
4. Soltar **BOOT**

### 3. Flashear

```bash
# Identificar puerto
ls /dev/ttyUSB*

# Borrar flash
uv run esptool.py --chip esp32 --port /dev/ttyUSB4 erase_flash

# Escribir firmware
uv run esptool.py --chip esp32 --port /dev/ttyUSB4 --baud 921600 \
  write_flash -z 0x1000 ESP32_GENERIC-20240602-v1.23.0.bin
```

### 4. Verificar

Conectar vía serial:
```bash
sudo screen /dev/ttyUSB0 115200
```
Presionar **Enter** — debe aparecer `>>>` (REPL de MicroPython).
Salir de screen: `Ctrl+A`, luego `:quit`, Enter.

## Conexiones HW-383 → NodeMCU

| HW-383   | SparkFun ESP32 Thing |
|----------|----------------------|
| **VCC**  | **3.3V**             |
| **RY-VCC** | **Vin** (~5V por USB) |
| **GND**  | **GND**              |
| **IN1**  | **GPIO22**          |
| **IN2**  | **GPIO23**          |

⚠️ **Importante:** el jumper entre VCC y RY-VCC del módulo debe estar **REMOVIDO**.
VCC va a 3.3V (lógica del optoacoplador) y RY-VCC a Vin (5V para las bobinas del relé).

## Firmware del ESP32

Subir `firmware/main.py` al ESP32:

```bash
mpremote connect /dev/ttyUSB4 cp firmware/main.py :main.py
mpremote connect /dev/ttyUSB4 reset
```

Presionar **RST** en la placa. Aparecerá el prompt `> `.

### Comandos seriales

| Comando    | Acción               |
|------------|----------------------|
| `1 on`     | Encender relé 1 (GPIO22) |
| `1 off`    | Apagar relé 1        |
| `2 on`     | Encender relé 2 (GPIO23) |
| `2 off`    | Apagar relé 2        |
| `all on`   | Encender ambos       |
| `all off`  | Apagar ambos         |
| `status`   | Estado actual        |

## Cliente para PC

```bash
# Auto-detecta el puerto (Linux / macOS)
uv run client/control_reles.py

# O especificar el puerto manualmente
uv run client/control_reles.py /dev/ttyUSB0   # Linux
uv run client/control_reles.py COM3           # Windows
```

Menú interactivo:
```
=== CONTROL DE RELES HW-383 ===

  1  -> Encender relé 1
  2  -> Apagar relé 1
  3  -> Encender relé 2
  4  -> Apagar relé 2
  5  -> Encender ambos
  6  -> Apagar ambos
  s  -> Estado actual
  q  -> Salir

Opcion:
```

Requiere permisos de escritura en el puerto serial. Si da error de permisos:
```bash
sudo usermod -aG uucp $USER
# Cerrar sesión y volver a entrar
```

O temporalmente:
```bash
sudo uv run client/control_reles.py
```

## Configuracion (.env)

Copiar `env.template` como `.env` y editar segun corresponda:

```bash
cp env.template .env
```

```ini
# .env
RELAY_PORT=8000            # Puerto del servidor REST
RELAY_HOST=127.0.0.1        # Host del servidor REST
SERIAL_PORT=                # Puerto serial (vacio = auto-detect)
```

El `.env` se **carga automáticamente** al arrancar el servidor — no hace falta pasarlo explícitamente.

Las variables tambien se pueden pasar directamente al comando (tienen prioridad sobre .env):
```bash
SERIAL_PORT=COM3 RELAY_PORT=9000 uv run uvicorn server.main:app
```

## Servidor REST API

El servidor **auto-detecta** el puerto serial al arrancar.

Inicio rápido (lee `.env` automáticamente):

```bash
uv run python -m server
```

Para desarrollo con hot-reload:

```bash
uv run python -m server --reload
```

O directamente con uvicorn (ignora .env):

```bash
uv run uvicorn server.main:app --host 127.0.0.1 --port 8000 --reload
```

### Endpoints

| Método | Ruta                     | Descripción                |
|--------|--------------------------|----------------------------|
| `GET`  | `/api/health`            | Estado de conexión         |
| `GET`  | `/api/relays`            | Estado de ambos relés      |
| `POST` | `/api/relays/1/on`       | Encender relé 1            |
| `POST` | `/api/relays/1/off`      | Apagar relé 1              |
| `POST` | `/api/relays/2/on`       | Encender relé 2            |
| `POST` | `/api/relays/2/off`      | Apagar relé 2              |
| `POST` | `/api/relays/all/on`     | Encender ambos             |
| `POST` | `/api/relays/all/off`    | Apagar ambos               |
| `POST` | `/api/direction/subir`   | Relé 1 ON, Relé 2 OFF      |
| `POST` | `/api/direction/bajar`   | Relé 1 OFF, Relé 2 ON      |
| `POST` | `/api/restart`            | Reinicia el servidor        |

Respuesta de ejemplo:
```json
{
  "relay_1": "ON",
  "relay_2": "OFF"
}
```

## Arranque automático

### Linux (systemd)

Para cambiar el puerto, editar `.env` y reiniciar:

```bash
# .env
RELAY_PORT=8080
```

```bash
systemctl --user restart psv-relay-server
```

**Instalar:**
```bash
sudo usermod -aG uucp $USER          # permisos serial (una vez, cerrar sesión)
bash deploy/install-service.sh        # instalar servicio
systemctl --user start psv-relay-server   # iniciar ahora
```

**Detener / deshabilitar:**
```bash
systemctl --user stop psv-relay-server          # detener ahora
systemctl --user disable psv-relay-server       # no arrancar al inicio
systemctl --user status psv-relay-server        # ver estado
journalctl --user -u psv-relay-server -f        # logs en vivo
```

### Windows (Tarea programada)

**Instalar:**
```powershell
powershell -ExecutionPolicy Bypass -File deploy\install-scheduled-task.ps1
Start-ScheduledTask -TaskName 'PSV-Relay-Server'   # iniciar ahora
```

**Detener / deshabilitar:**
```powershell
Stop-ScheduledTask -TaskName 'PSV-Relay-Server'        # detener ahora
Disable-ScheduledTask -TaskName 'PSV-Relay-Server'     # no arrancar al inicio
Get-ScheduledTask -TaskName 'PSV-Relay-Server' | Get-ScheduledTaskInfo  # ver estado
```

O desde `taskschd.msc` (Win+R, escribir `taskschd.msc`).

**Uso manual (sin instalación):** ejecutar `deploy\start-server.bat`.

## Archivos del proyecto

```
psv-elevation-control/
├── README.md                       # Este archivo
├── pyproject.toml                  # Proyecto Python
├── firmware/
│   └── main.py                     # Firmware MicroPython para NodeMCU
├── client/
│   └── control_reles.py            # Cliente interactivo para PC
├── server/
│   ├── main.py                     # Servidor REST FastAPI
│   └── serial_service.py           # Servicio de comunicación serial
└── deploy/
    ├── psv-relay-server.service    # systemd (Linux)
    ├── install-service.sh          # Instalador Linux
    ├── install-scheduled-task.ps1  # Tarea programada (Windows)
    └── start-server.bat            # Inicio manual (Windows)
```
