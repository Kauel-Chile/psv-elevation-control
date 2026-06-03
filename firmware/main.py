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
    STAT_LED = 5  # LED azul STAT en SparkFun ESP32 Thing
    machine.freq(80000000)  # Solo control de reles, no necesita 240 MHz
except ImportError:
    R1 = 5
    R2 = 4
    LS1 = 18
    LS2 = 19
    STAT_LED = None
    machine.freq(80000000)

r1 = machine.Pin(R1, machine.Pin.OUT, value=1)
r2 = machine.Pin(R2, machine.Pin.OUT, value=1)
ls1 = machine.Pin(LS1, machine.Pin.IN, machine.Pin.PULL_UP)
ls2 = machine.Pin(LS2, machine.Pin.IN, machine.Pin.PULL_UP)
if STAT_LED is not None:
    machine.Pin(STAT_LED, machine.Pin.OUT, value=0)  # Apagar STAT LED

import sys
import select

poll = select.poll()
poll.register(sys.stdin, select.POLLIN)


# Estado anterior de los switches para deteccion de flanco
_ls1_prev = 1
_ls2_prev = 1


def read_limits():
    """Lee switches y detecta flancos descendentes (switch se cierra).
    Cuando un switch se cierra, fuerza OFF el relay correspondiente.
    Retorna: 0=ninguno, 1=limite1 activo, 2=limite2 activo, 3=ambos"""
    global _ls1_prev, _ls2_prev
    flags = 0

    v1 = ls1.value()
    v2 = ls2.value()

    if v1 == 0:
        flags |= 1
        if _ls1_prev == 1:  # flanco descendente → switch acaba de cerrarse
            r1.value(1)  # fuerza OFF rele 1
    if v2 == 0:
        flags |= 2
        if _ls2_prev == 1:  # flanco descendente → switch acaba de cerrarse
            r2.value(1)  # fuerza OFF rele 2

    _ls1_prev = v1
    _ls2_prev = v2
    return flags


def f(v):
    return "ON" if v == 0 else "OFF"


sys.stdout.write(">")
b = ""
while True:
    # Detectar flanco descendente (switch se cierra → fuerza OFF relay)
    read_limits()

    events = poll.poll(100)
    if not events:
        continue

    c = sys.stdin.read(1)
    if not c:
        continue

    if c in "\r\n":
        if b:
            s = b.strip().lower()
            limites = read_limits()  # re-verificar al procesar comando

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
                # Siempre retorna estado real + info de limites
                sys.stdout.write(
                    "\r\n1="
                    + f(r1.value())
                    + " 2="
                    + f(r2.value())
                    + " LS="
                    + str(limites)
                    + "\r\n>"
                )
            else:
                sys.stdout.write("\r\n?\r\n>")
            b = ""
    else:
        b += c
