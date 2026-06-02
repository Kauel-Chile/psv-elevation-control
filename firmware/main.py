"""
Firmware para control de reles HW-383
Compatible: ESP32 y ESP8266 (NodeMCU)
Switches de limite por rele:
  GPIO18 = Limite 1 (bloquea rele 1, solo permite bajar)
  GPIO19 = Limite 2 (bloquea rele 2, solo permite subir)
"""

import machine

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
ls1 = machine.Pin(LS1, machine.Pin.IN, machine.Pin.PULL_UP)
ls2 = machine.Pin(LS2, machine.Pin.IN, machine.Pin.PULL_UP)

import sys
import select

poll = select.poll()
poll.register(sys.stdin, select.POLLIN)


def check_limits():
    """Verifica ambos limites. Fuerza OFF el rele correspondiente.
    Retorna: 0=ninguno, 1=limite1 activo, 2=limite2 activo, 3=ambos"""
    flags = 0
    if ls1.value() == 0:
        r1.value(1)
        flags |= 1
    if ls2.value() == 0:
        r2.value(1)
        flags |= 2
    return flags


def f(v):
    return "ON" if v == 0 else "OFF"


sys.stdout.write(">")
b = ""
while True:
    # Verificar limites siempre (fuerza OFF los reles)
    check_limits()

    events = poll.poll(100)
    if not events:
        continue

    c = sys.stdin.read(1)
    if not c:
        continue

    if c in "\r\n":
        if b:
            s = b.strip().lower()
            limites = check_limits()  # re-verificar al procesar comando

            if s == "1 on":
                if limites & 1:
                    sys.stdout.write("\r\n!LIMITE1\r\n>")
                else:
                    r1.value(0)
                    sys.stdout.write("\r\nOK 1=ON 2=" + f(r2.value()) + "\r\n>")
            elif s == "1 off":
                r1.value(1)
                sys.stdout.write("\r\nOK 1=OFF 2=" + f(r2.value()) + "\r\n>")
            elif s == "2 on":
                if limites & 2:
                    sys.stdout.write("\r\n!LIMITE2\r\n>")
                else:
                    r2.value(0)
                    sys.stdout.write("\r\nOK 1=" + f(r1.value()) + " 2=ON\r\n>")
            elif s == "2 off":
                r2.value(1)
                sys.stdout.write("\r\nOK 1=" + f(r1.value()) + " 2=OFF\r\n>")
            elif s == "all on":
                if limites & 1 and limites & 2:
                    sys.stdout.write("\r\n!LIMITE\r\n>")
                elif limites & 1:
                    sys.stdout.write("\r\n!LIMITE1\r\n>")
                elif limites & 2:
                    sys.stdout.write("\r\n!LIMITE2\r\n>")
                else:
                    r1.value(0)
                    r2.value(0)
                    sys.stdout.write("\r\nOK 1=ON 2=ON\r\n>")
            elif s == "all off":
                r1.value(1)
                r2.value(1)
                sys.stdout.write("\r\nOK 1=OFF 2=OFF\r\n>")
            elif s == "status":
                if limites:
                    sys.stdout.write("\r\n1=OFF 2=OFF\r\n>")
                else:
                    sys.stdout.write(
                        "\r\n1=" + f(r1.value()) + " 2=" + f(r2.value()) + "\r\n>"
                    )
            else:
                sys.stdout.write("\r\n?\r\n>")
            b = ""
    else:
        b += c
