# /// script
# dependencies = ["pyserial"]
# ///
"""
Cliente para PC — Control de relés HW-383 vía NodeMCU (ESP8266)

Uso:
    uv run client/control_reles.py [puerto]

Si no se pasa puerto, auto-detecta el primer CH340/CP210x/FTDI.
En Windows ej: uv run client/control_reles.py COM3
"""

import sys
import time

import serial
import serial.tools.list_ports


_RECV_TIMEOUT = 0.5

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


def auto_detectar() -> str | None:
    """Busca el primer puerto con chip CH340, CP210x o FTDI."""
    for puerto in serial.tools.list_ports.comports():
        if puerto.vid in (0x1A86, 0x10C4, 0x0403):
            return puerto.device
    return None


def conectar(puerto: str) -> serial.Serial | None:
    try:
        ser = serial.Serial(puerto, BAUD, timeout=_RECV_TIMEOUT)
        time.sleep(1.5)
        ser.reset_input_buffer()
        return ser
    except serial.SerialException as e:
        print(f"  Error: {e}")
        return None


def enviar(ser: serial.Serial, cmd: str) -> str:
    ser.write((cmd + "\r\n").encode())
    # Esperar primer byte (timeout del serial maneja la pausa)
    first = ser.read(1)
    if not first:
        return ""
    # 5ms para que llegue el resto del paquete
    time.sleep(0.005)
    rest = ser.read(ser.in_waiting or 1)
    return (first + rest).decode(errors="replace").strip()


def main():
    puerto = sys.argv[1] if len(sys.argv) > 1 else auto_detectar()
    if not puerto:
        print("No se encontró el NodeMCU.")
        print("Usá: uv run client/control_reles.py <PUERTO>")
        print("  Linux:   /dev/ttyUSB0")
        print("  Windows: COM3")
        sys.exit(1)

    print(f" Conectando a {puerto}...", end=" ")
    sys.stdout.flush()

    ser = conectar(puerto)
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
