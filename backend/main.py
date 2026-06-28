"""FastAPI backend for Lab-Ninja.

All business logic lives in pluggable modules under modules/.
This file is purely application wiring.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.common import __version__
from modules.common.db import init_db

# Lab modules
from modules.dsa_lab.router import router as dsa_router
from modules.cv_lab.router import router as cv_router
from modules.system_design_lab.router import router as sd_router

# Daily session module
from modules.daily_session.daily_session import router as session_router


app = FastAPI(title="Lab-Ninja API", version=__version__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session_router)
app.include_router(dsa_router)
app.include_router(cv_router)
app.include_router(sd_router)


@app.on_event("startup")
async def _startup() -> None:  # pragma: no cover
    init_db()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "lab-ninja-api", "version": __version__}


# To run locally:
#   uvicorn main:app --reload --port 8000  (from backend/)
