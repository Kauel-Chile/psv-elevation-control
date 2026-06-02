"""
Firmware para control de reles HW-383
Compatible: ESP32 y ESP8266 (NodeMCU)
Switches de limite en GPIO18 y GPIO19 (activos en LOW)
"""
import machine

try:
    import esp32
    R1 = 22; R2 = 23; LS1 = 18; LS2 = 19
except ImportError:
    R1 = 5; R2 = 4; LS1 = 18; LS2 = 19
    machine.freq(80000000)

r1 = machine.Pin(R1, machine.Pin.OUT, value=1)
r2 = machine.Pin(R2, machine.Pin.OUT, value=1)
ls1 = machine.Pin(LS1, machine.Pin.IN, machine.Pin.PULL_UP)
ls2 = machine.Pin(LS2, machine.Pin.IN, machine.Pin.PULL_UP)

import sys
import select
poll = select.poll()
poll.register(sys.stdin, select.POLLIN)


def limit_off():
    """Si algun switch activo, apagar rele y True."""
    if ls1.value() == 0 or ls2.value() == 0:
        r1.value(1)
        r2.value(1)
        return True
    return False


def f(v):
    return "ON" if v == 0 else "OFF"


sys.stdout.write(">")
b = ""
while True:
    events = poll.poll(100)
    if not events:
        continue

    c = sys.stdin.read(1)
    if not c:
        continue

    if c in "\r\n":
        if b:
            s = b.strip().lower()
            # Si hay limite, apagar y bloquear "on"
            if limit_off() and "on" in s:
                sys.stdout.write("\r\n!LIMITE\r\n>")
            elif s == "1 on":
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
                if limit_off():
                    sys.stdout.write("\r\n1=OFF 2=OFF\r\n>")
                else:
                    sys.stdout.write("\r\n1=" + f(r1.value()) + " 2=" + f(r2.value()) + "\r\n>")
            else:
                sys.stdout.write("\r\n?\r\n>")
            b = ""
    else:
        b += c
