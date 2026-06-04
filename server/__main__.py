"""
Entry point programático para el servidor REST.
Carga .env automaticamente y pasa RELAY_HOST/RELAY_PORT a uvicorn.

Uso:
    uv run python -m server

    # Lee RELAY_HOST/RELAY_PORT de .env (o entorno)
    # Si no estan seteados: 127.0.0.1:8000
"""

import os
import sys

# Cargar .env antes de importar uvicorn
from dotenv import load_dotenv

load_dotenv()

import uvicorn

HOST = os.environ.get("RELAY_HOST", "127.0.0.1")
PORT = int(os.environ.get("RELAY_PORT", "8000"))

if __name__ == "__main__":
    uvicorn.run(
        "server.main:app",
        host=HOST,
        port=PORT,
        reload="--reload" in sys.argv or "-r" in sys.argv,
    )
