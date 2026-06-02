"""
Firmware para control de relés HW-383
Compatible: ESP32 y ESP8266 (NodeMCU)
Switches de limite en GPIO18 y GPIO19 (activos en LOW)
Si cualquier switch se activa, ambos reles se apagan.
"""

import machine

# Auto-detectar placa y configurar pines
try:
    import esp32

    R1 = 22
    R2 = 23
    LS1 = 18
    LS2 = 19
except ImportError:
    R1 = 5
    R2 = 4
    LS1 = 18
    LS2 = 19
    machine.freq(80000000)

r1 = machine.Pin(R1, machine.Pin.OUT, value=1)
r2 = machine.Pin(R2, machine.Pin.OUT, value=1)

# Switches de limite (activos en LOW, con pull-up interno)
ls1 = machine.Pin(LS1, machine.Pin.IN, machine.Pin.PULL_UP)
ls2 = machine.Pin(LS2, machine.Pin.IN, machine.Pin.PULL_UP)

import sys
import select

poll = select.poll()
poll.register(sys.stdin, select.POLLIN)


def f(v):
    return "ON" if v == 0 else "OFF"


def check_limits():
    """Si algun switch esta activo, apagar todo."""
    if ls1.value() == 0 or ls2.value() == 0:
        r1.value(1)
        r2.value(1)
        return True
    return False


sys.stdout.write(">")
b = ""
while True:
    # Verificar switches de limite
    if check_limits():
        # Leer todos los bytes disponibles SIN perder b
        events = poll.poll(10)
        while events:
            while events:
                c = sys.stdin.read(1)
                if not c:
                    break
                if c in "\r\n":
                    if b:
                        s = b.strip().lower()
                        if s == "status":
                            sys.stdout.write("\r\n1=OFF 2=OFF\r\n>")
                        elif "off" in s or s == "?":
                            sys.stdout.write("\r\nOK 1=OFF 2=OFF\r\n>")
                        elif "on" in s:
                            sys.stdout.write("\r\n!LIMITE\r\n>")
                        else:
                            sys.stdout.write("\r\n?\r\n>")
                        b = ""
                else:
                    b += c
                events = poll.poll(0)
            # Esperar un poco por si llegan mas bytes
            events = poll.poll(5)
        # Sin datos: solo !LIMITE, NO resetear b
        if not b:
            sys.stdout.write("\r\n!LIMITE\r\n>")
        continue

    # Esperar dato del serial (no bloquea por mas de 100ms)
    events = poll.poll(100)
    if not events:
        continue

    c = sys.stdin.read(1)
    if not c:
        continue

    if c in "\r\n":
        if b:
            s = b.strip().lower()

            # Re-verificar switches antes de cualquier comando "on"
            if check_limits():
                sys.stdout.write("\r\n!LIMITE\r\n>")
                b = ""
                continue

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
