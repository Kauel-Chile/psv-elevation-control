# /// script
# dependencies = ["pyserial"]
# ///
"""Sube firmware byte a byte con pacing lento (10ms)."""

import sys
import time
import base64
import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB4"

with open("firmware/main.py") as f:
    code = f.read()

b64 = base64.b64encode(code.encode()).decode()

# Comando para escribir main.py desde base64
# Usamos nombre de variable corto para minimizar bytes
cmd = (
    "import binascii\nf=open('main.py','wb')\nf.write(binascii.a2b_base64('"
    + b64
    + "'))\nf.close()\nprint('OK')\n"
)

print(f"Subiendo {len(cmd)} bytes con pacing 10ms...")

ser = serial.Serial()
ser.port = PORT
ser.baudrate = 115200
ser.timeout = 1
ser.dtr = False
ser.rts = False
time.sleep(0.3)
ser.open()
time.sleep(1)
ser.dtr = False
time.sleep(0.3)
ser.reset_input_buffer()

# Entrar en raw REPL
ser.write(b"\x01")
time.sleep(0.5)
ser.reset_input_buffer()

# Enviar con pacing de 10ms ENTRE CADA BYTE
dat = cmd.encode()
for b in dat:
    ser.write(bytes([b]))
    time.sleep(0.01)  # 10ms entre bytes

print(f"Enviados {len(dat)} bytes en {len(dat) * 0.01:.1f}s")

# Ejecutar
time.sleep(0.2)
ser.write(b"\x04")
time.sleep(2)
r = ser.read(2000).decode(errors="replace")
print(f"Res: {r[:200]}")

# Soft reset
time.sleep(0.1)
ser.write(b"\x04")
time.sleep(2)
r = ser.read(2000).decode(errors="replace")
print(f"Boot: {r[:200]}")
ser.close()
