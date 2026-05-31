import machine

r1 = machine.Pin(22, machine.Pin.OUT, value=1)
r2 = machine.Pin(23, machine.Pin.OUT, value=1)


def f(v):
    return "ON" if v == 0 else "OFF"


import sys

b = ""
sys.stdout.write(">")
while True:
    c = sys.stdin.read(1)
    if c in "\r\n":
        if b:
            s = b.strip().lower()
            if "1 on" == s:
                r1.value(0)
                sys.stdout.write("\r\nOK 1=ON 2=" + f(r2.value()) + "\r\n>")
            elif "1 off" == s:
                r1.value(1)
                sys.stdout.write("\r\nOK 1=OFF 2=" + f(r2.value()) + "\r\n>")
            elif "2 on" == s:
                r2.value(0)
                sys.stdout.write("\r\nOK 1=" + f(r1.value()) + " 2=ON\r\n>")
            elif "2 off" == s:
                r2.value(1)
                sys.stdout.write("\r\nOK 1=" + f(r1.value()) + " 2=OFF\r\n>")
            elif "all on" == s:
                r1.value(0)
                r2.value(0)
                sys.stdout.write("\r\nOK 1=ON 2=ON\r\n>")
            elif "all off" == s:
                r1.value(1)
                r2.value(1)
                sys.stdout.write("\r\nOK 1=OFF 2=OFF\r\n>")
            elif "status" == s:
                sys.stdout.write(
                    "\r\n1=" + f(r1.value()) + " 2=" + f(r2.value()) + "\r\n>"
                )
            else:
                sys.stdout.write("\r\n?\r\n>")
        b = ""
    else:
        b += c
