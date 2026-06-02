"""
Servicio de comunicación serial con el NodeMCU.
Maneja la conexión, envío de comandos y parsing de respuestas.
"""

import contextlib
import logging
import time

import serial
import serial.tools.list_ports

logger = logging.getLogger(__name__)

BAUD = 115200
TIMEOUT = 0.5


class SerialRelayService:
    def __init__(self, puerto: str | None = None):
        self._puerto = puerto
        self._ser: serial.Serial | None = None

    # ── Gestión de conexión ────────────────────────────────

    @property
    def conectado(self) -> bool:
        return self._ser is not None and self._ser.is_open

    def conectar(self, puerto: str | None = None) -> str | None:
        """Conecta al puerto indicado (o auto-detecta). Devuelve error o None."""
        if self.conectado:
            self.desconectar()

        target = puerto or self._puerto or self._auto_detectar()
        if not target:
            return "No se encontró ningún puerto serial (CH340/CP210x/FTDI)"

        try:
            # Abrir sin tocar DTR/RTS (evita reset del ESP32)
            self._ser = serial.Serial()
            self._ser.port = target
            self._ser.baudrate = BAUD
            self._ser.timeout = TIMEOUT
            self._ser.write_timeout = 1
            self._ser.dsrdtr = False
            self._ser.rtscts = False
            self._ser.dtr = False
            self._ser.rts = False
            time.sleep(0.3)
            self._ser.open()
            time.sleep(0.5)
            self._ser.dtr = False
            self._ser.rts = False
            # Esperar boot del ESP32 y descartar boot message
            time.sleep(2)
            self._ser.reset_input_buffer()
            self._puerto = target
            logger.info("Conectado a %s", target)
            return None
        except serial.SerialException as e:
            self._ser = None
            return f"No se pudo conectar a {target}: {e}"

    def desconectar(self):
        if self._ser:
            with contextlib.suppress(Exception):
                self._ser.close()
            self._ser = None
            logger.info("Desconectado")

    @staticmethod
    def _auto_detectar() -> str | None:
        """Busca el primer puerto serial con chip CH340, CP210x o FTDI."""
        for puerto in serial.tools.list_ports.comports():
            if puerto.vid in (0x1A86, 0x10C4, 0x0403):  # CH340, CP210x, FTDI
                logger.info(
                    "Auto-detectado: %s (%s)", puerto.device, puerto.description
                )
                return puerto.device
        return None

    # ── Comandos ───────────────────────────────────────────

    def _serial(self) -> serial.Serial:
        if not self._ser:
            raise RuntimeError("Serial no conectado")
        return self._ser

    def enviar(self, comando: str) -> str | None:
        """Envía un comando y devuelve la respuesta. None si hay error."""
        try:
            ser = self._serial()

            # Descartar cualquier dato residual del buffer (ej: !LIMITE)
            ser.reset_input_buffer()

            ser.write((comando + "\r\n").encode())

            # Leer hasta el prompt ">" o timeout
            resp = ser.read_until(b">", 100).decode(errors="replace")
            # Limpiar: sacar \r\n, espacios y el ">" final
            resp = resp.strip().rstrip(">").strip()
            return resp if resp else None
        except Exception as e:
            logger.error("Error al enviar comando: %s", e)
            return None

    # ── Comandos específicos ───────────────────────────────

    def encender(self, rele: int) -> str | None:
        return self.enviar(f"{rele} on")

    def apagar(self, rele: int) -> str | None:
        return self.enviar(f"{rele} off")

    def encender_todo(self) -> str | None:
        return self.enviar("all on")

    def apagar_todo(self) -> str | None:
        return self.enviar("all off")

    def estado(self) -> dict | None:
        """Devuelve dict con estados de los relés, o None."""
        resp = self.enviar("status")
        if not resp:
            return None
        # Parsear "1=ON 2=OFF"
        try:
            partes = resp.split()
            d = {}
            for p in partes:
                if "=" in p:
                    k, v = p.split("=")
                    d[f"relay_{k}"] = v
            return d if d else None
        except Exception:
            return None
