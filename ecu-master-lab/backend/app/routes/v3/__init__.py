from __future__ import annotations

from fastapi import APIRouter

from app.routes.v3.modification import router as modification_router

v3_router = APIRouter()
v3_router.include_router(modification_router)
