# PSV Elevation Control

Control de relés HW-383 con NodeMCU (ESP8266) + MicroPython.

## Requisitos

- NodeMCU (ESP8266)
- Módulo de relés HW-383 (2 canales)
- Cable USB con datos
- `esptool` y `mpremote` instalados:
  ```bash
  uv tool install esptool
  uv tool install mpremote
  ```

## Instalación de MicroPython en NodeMCU

### 1. Descargar firmware

Última versión estable para ESP8266 desde [micropython.org](https://micropython.org/download/ESP8266_GENERIC/).

O directamente:
```bash
curl -LO https://micropython.org/resources/firmware/ESP8266_GENERIC-20260406-v1.28.0.bin
```

### 2. Poner NodeMCU en modo flash

1. Mantener presionado **FLASH**
2. Presionar **RST** (sin soltar FLASH)
3. Soltar **RST**
4. Soltar **FLASH**

### 3. Flashear

```bash
# Identificar puerto
ls /dev/ttyUSB*

# Borrar flash
sudo env "PATH=$PATH" esptool --port /dev/ttyUSB0 erase_flash

# Escribir firmware
sudo env "PATH=$PATH" esptool --port /dev/ttyUSB0 --baud 460800 write_flash \
  --flash_size=detect 0x0 ESP8266_GENERIC-20260406-v1.28.0.bin
```

### 4. Verificar

Conectar vía serial:
```bash
sudo screen /dev/ttyUSB0 115200
```
Presionar **Enter** — debe aparecer `>>>` (REPL de MicroPython).
Salir de screen: `Ctrl+A`, luego `:quit`, Enter.

## Conexiones HW-383 → NodeMCU

| HW-383   | NodeMCU       |
|----------|---------------|
| **VCC**  | **3.3V**      |
| **RY-VCC** | **Vin** (~5V por USB) |
| **GND**  | **GND**       |
| **IN1**  | **D1** (GPIO5) |
| **IN2**  | **D2** (GPIO4) |

⚠️ **Importante:** el jumper entre VCC y RY-VCC del módulo debe estar **REMOVIDO**.
VCC va a 3.3V (lógica del optoacoplador) y RY-VCC a Vin (5V para las bobinas).

## Firmware del NodeMCU

Subir `firmware/main.py` al NodeMCU:

```bash
sudo env "PATH=$PATH" mpremote connect /dev/ttyUSB0 cp firmware/main.py :main.py
```

Presionar **RST** para reiniciar. Aparecerá el prompt de comandos `> `.

### Comandos seriales

| Comando    | Acción               |
|------------|----------------------|
| `1 on`     | Encender relé 1      |
| `1 off`    | Apagar relé 1        |
| `2 on`     | Encender relé 2      |
| `2 off`    | Apagar relé 2        |
| `all on`   | Encender ambos       |
| `all off`  | Apagar ambos         |
| `status`   | Estado actual        |

## Cliente para PC

```bash
uv run client/control_reles.py
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

## Archivos del proyecto

```
psv-elevation-control/
├── README.md               # Este archivo
├── firmware/
│   └── main.py             # Firmware MicroPython para NodeMCU
├── client/
│   └── control_reles.py    # Cliente interactivo para PC
└── pyproject.toml          # Proyecto Python
```
