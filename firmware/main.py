"""
Firmware para control de relés HW-383
Compatible: ESP32 y ESP8266 (NodeMCU)
Detección automática de pines según la placa.
"""

import machine

# Auto-detectar placa y configurar pines
try:
    import esp32  # Solo existe en ESP32

    R1 = 22
    R2 = 23
    FREQ = 240000000  # ESP32 a velocidad normal
except ImportError:
    # ESP8266: reducir frecuencia para evitar brownout
    R1 = 5  # D1
    R2 = 4  # D2
    machine.freq(80000000)

r1 = machine.Pin(R1, machine.Pin.OUT, value=1)
r2 = machine.Pin(R2, machine.Pin.OUT, value=1)


def f(v):
    return "ON" if v == 0 else "OFF"


import sys

sys.stdout.write(">")
b = ""
while True:
    c = sys.stdin.read(1)
    if c in "\r\n":
        if b:
            s = b.strip().lower()
            if s == "1 on":
                r1.value(0)
                sys.stdout.write("\r\nOK 1=ON 2=" + f(r2.value()) + "\r\n>")
            elif s == "1 off":
                r1.value(1)
                sys.stdout.write("\r\nOK 1=OFF 2=" + f(r2.value()) + "\r\n>")
            elif s == "2 on":
                r2.value(0)
                sys.stdout.write("\r\nOK 1=" + f(r1.value()) + " 2=ON\r\n>")
            elif s == "2 off":
                r2.value(1)
                sys.stdout.write("\r\nOK 1=" + f(r1.value()) + " 2=OFF\r\n>")
            elif s == "all on":
                r1.value(0)
                r2.value(0)
                sys.stdout.write("\r\nOK 1=ON 2=ON\r\n>")
            elif s == "all off":
                r1.value(1)
                r2.value(1)
                sys.stdout.write("\r\nOK 1=OFF 2=OFF\r\n>")
            elif s == "status":
                sys.stdout.write(
                    "\r\n1=" + f(r1.value()) + " 2=" + f(r2.value()) + "\r\n>"
                )
            else:
                sys.stdout.write("\r\n?\r\n>")
        b = ""
    else:
        b += c
