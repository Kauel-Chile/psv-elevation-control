# /// script
# dependencies = ["pyserial"]
# ///
"""
Cliente para PC — Control de relés HW-383 vía NodeMCU (ESP8266)

Uso:
    uv run client/control_reles.py

Requiere: pyserial (se instala automáticamente con uv)
"""

import serial
import sys
import time

PORT = "/dev/ttyUSB1"
BAUD = 115200

COMANDOS = {
    "1": ("1 on", "Encender relé 1"),
    "2": ("1 off", "Apagar relé 1"),
    "3": ("2 on", "Encender relé 2"),
    "4": ("2 off", "Apagar relé 2"),
    "5": ("all on", "Encender ambos"),
    "6": ("all off", "Apagar ambos"),
    "s": ("status", "Estado actual"),
}


def conectar(puerto: str) -> serial.Serial | None:
    try:
        ser = serial.Serial(puerto, BAUD, timeout=2)
        time.sleep(1.5)
        ser.reset_input_buffer()
        return ser
    except serial.SerialException as e:
        print(f"  Error: {e}")
        return None


def enviar(ser: serial.Serial, cmd: str) -> str:
    ser.write((cmd + "\r\n").encode())
    time.sleep(0.2)
    resp = ser.read(1024).decode(errors="replace").strip()
    return resp


def main():

    print()
    print(f" Conectando a {PORT}...", end=" ")
    sys.stdout.flush()

    ser = conectar(PORT)
    if not ser:
        sys.exit(1)

    ser.reset_input_buffer()
    print("conectado")
    print()

    while True:
        print()
        print("=== CONTROL DE RELES HW-383 ===")
        print()
        for key, (_cmd, desc) in COMANDOS.items():
            print(f"  {key}  -> {desc}")
        print("  q  -> Salir")
        print()

        opcion = input("Opcion: ").strip().lower()

        if opcion == "q":
            print("Chau!")
            break

        if opcion not in COMANDOS:
            print("  Opcion invalida")
            continue

        cmd, desc = COMANDOS[opcion]
        resp = enviar(ser, cmd)

        if "1=" in resp:
            idx_est = resp.find("1=")
            estado = resp[idx_est:] if idx_est >= 0 else resp
            print(f"  {desc} -> {estado}")
        else:
            print(f"  {desc} -> {resp.strip()}")

    ser.close()


if __name__ == "__main__":
    main()
