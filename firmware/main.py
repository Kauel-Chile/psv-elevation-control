"""
Firmware para NodeMCU (ESP8266) - Control de relés HW-383
Conexiones:
  HW-383         NodeMCU
  VCC     →      3.3V
  RY-VCC  →      Vin
  GND     →      GND
  IN1     →      D1 (GPIO5)
  IN2     →      D2 (GPIO4)

Comandos seriales: 1 on | 1 off | 2 on | 2 off | all on | all off | status
"""

import sys
import machine
import time

try:
    import select

    USESELECT = True
except:
    USESELECT = False

# --- Pines ---
r1 = machine.Pin(5, machine.Pin.OUT)
r2 = machine.Pin(4, machine.Pin.OUT)
r1.value(1)
r2.value(1)


def estado() -> str:
    a = "ON" if r1.value() == 0 else "OFF"
    b = "ON" if r2.value() == 0 else "OFF"
    return "1={} 2={}".format(a, b)


def procesar(linea: str) -> str:
    s = linea.strip().lower()
    if s == "1 on":
        r1.value(0)
    elif s == "1 off":
        r1.value(1)
    elif s == "2 on":
        r2.value(0)
    elif s == "2 off":
        r2.value(1)
    elif s == "all on":
        r1.value(0)
        r2.value(0)
    elif s == "all off":
        r1.value(1)
        r2.value(1)
    elif s == "status":
        return estado()
    else:
        return "? " + s
    return "OK " + estado()


# --- Bienvenida ---
sys.stdout.write("\r\n=== RELES HW-383 ===\r\n")
sys.stdout.write(
    "Comandos: 1 on | 1 off | 2 on | 2 off | all on | all off | status\r\n"
)

# --- Loop principal ---
buf = ""
while True:
    sys.stdout.write("> ")
    buf = ""

    while True:
        hay = False
        if USESELECT:
            r, _, _ = select.select([sys.stdin], [], [], 0.005)
            hay = len(r) > 0

        if hay:
            c = sys.stdin.read(1)
            if c:
                if c == "\r" or c == "\n":
                    if buf:
                        sys.stdout.write("\r\n")
                        sys.stdout.write(procesar(buf))
                        sys.stdout.write("\r\n")
                        break
                else:
                    buf += c

        time.sleep_ms(5)
