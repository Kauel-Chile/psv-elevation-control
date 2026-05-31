# /// script
# dependencies = ["pyserial"]
# ///
"""Sube firmware como base64 y lo guarda como main.py con pacing."""

import sys
import time
import base64
import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB4"

with open("firmware/main.py") as f:
    code = f.read()

b64 = base64.b64encode(code.encode()).decode()

# Comando: escribir main.py desde base64 e importar
cmd = (
    "import binascii,os\n"
    "f=open('main.py','wb')\n"
    "f.write(binascii.a2b_base64('" + b64 + "'))\n"
    "f.close()\n"
    "import main\n"
)

print(f"Subiendo {len(cmd)} chars a {PORT}...")

ser = serial.Serial()
ser.port = PORT
ser.baudrate = 115200
ser.timeout = 2
ser.dtr = False
ser.rts = False
time.sleep(0.3)
ser.open()
time.sleep(1)
ser.dtr = False
time.sleep(0.3)
ser.reset_input_buffer()

# Borrar main.py viejo
ser.write(b"import os\nos.remove('main.py')\n")
time.sleep(0.5)
ser.read(500)
ser.reset_input_buffer()

# Entrar en raw REPL
ser.write(b"\x01")
time.sleep(0.3)
ser.read(500)

# Enviar con pacing
dat = cmd.encode()
for i, b in enumerate(dat):
    ser.write(bytes([b]))
    time.sleep(0.003)

print(f"Enviados {len(dat)} bytes")

# Ejecutar (Ctrl+D)
ser.write(b"\x04")
time.sleep(2)
r = ser.read(3000)
print(f"Res: {r.decode(errors='replace')[:300]}")

# Soft reset para probar
time.sleep(0.3)
ser.write(b"\x04")
time.sleep(2)
r = ser.read(2000)
print(f"Boot: {r.decode(errors='replace')[:200]}")
ser.close()
print("OK")
