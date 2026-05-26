"""
Servidor REST para control de relés HW-383 vía NodeMCU.

Endpoints:
  GET  /api/health          → verificación de conexión
  GET  /api/relays           → estado de ambos relés
  POST /api/relays/{n}/on   → encender relé n (1 o 2)
  POST /api/relays/{n}/off  → apagar relé n
  POST /api/relays/all/on   → encender ambos
  POST /api/relays/all/off  → apagar ambos

Uso:
    uv run uvicorn server.main:app --reload --host 127.0.0.1 --port 8000
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from server.serial_service import SerialRelayService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Estado global ───────────────────────────────────────────

relay_service = SerialRelayService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Conecta al NodeMCU al iniciar, desconecta al cerrar."""
    error = relay_service.conectar()
    if error:
        logger.warning("⚠️  %s", error)
    else:
        logger.info("✅ Conectado al NodeMCU")
    yield
    relay_service.desconectar()
    logger.info("Desconectado del NodeMCU")


app = FastAPI(
    title="PSV Relay Control API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ─────────────────────────────────────────────────

class RelayStatus(BaseModel):
    relay_1: str
    relay_2: str


class HealthResponse(BaseModel):
    status: str
    puerto: str | None
    relays: RelayStatus | None


class ErrorResponse(BaseModel):
    detail: str


# ── Endpoints ───────────────────────────────────────────────

@app.get("/api/health", response_model=HealthResponse)
async def health():
    estado = relay_service.estado()
    return HealthResponse(
        status="ok" if relay_service.conectado else "disconnected",
        puerto=relay_service._puerto,
        relays=RelayStatus(**estado) if estado else None,
    )


@app.get("/api/relays", response_model=RelayStatus)
async def get_relays():
    estado = relay_service.estado()
    if not estado:
        raise HTTPException(503, "NodeMCU no conectado o no responde")
    return RelayStatus(**estado)


@app.post("/api/relays/{n}/on", response_model=RelayStatus)
@app.post("/api/relays/all/on", response_model=RelayStatus)
async def relay_on(n: int | None = None):
    if n is not None and n not in (1, 2):
        raise HTTPException(400, "Relé inválido (usar 1 o 2)")

    if n is not None:
        relay_service.encender(n)
    else:
        relay_service.encender_todo()

    estado = relay_service.estado()
    if not estado:
        raise HTTPException(503, "NodeMCU no responde")
    return RelayStatus(**estado)


@app.post("/api/relays/{n}/off", response_model=RelayStatus)
@app.post("/api/relays/all/off", response_model=RelayStatus)
async def relay_off(n: int | None = None):
    if n is not None and n not in (1, 2):
        raise HTTPException(400, "Relé inválido (usar 1 o 2)")

    if n is not None:
        relay_service.apagar(n)
    else:
        relay_service.apagar_todo()

    estado = relay_service.estado()
    if not estado:
        raise HTTPException(503, "NodeMCU no responde")
    return RelayStatus(**estado)
