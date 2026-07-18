from __future__ import annotations

from fastapi import APIRouter

from app.routes.v2.referentiel import router as referentiel_router
from app.routes.v2.vehicles import router as vehicles_router
from app.routes.v2.versions import router as versions_router
from app.routes.v2.memory import router as memory_router
from app.routes.v2.signatures import router as signatures_router
from app.routes.v2.maps import router as maps_router
from app.routes.v2.analysis import router as analysis_router
from app.routes.v2.ai import router as ai_router
from app.routes.v2.reports import router as reports_router
from app.routes.v2.activity import router as activity_router
from app.routes.v2.knowledge import router as knowledge_router

v2_router = APIRouter(prefix="/api", tags=["V2 - ECU Master Lab"])
v2_router.include_router(referentiel_router)
v2_router.include_router(vehicles_router)
v2_router.include_router(versions_router)
v2_router.include_router(memory_router)
v2_router.include_router(signatures_router)
v2_router.include_router(maps_router)
v2_router.include_router(analysis_router)
v2_router.include_router(ai_router)
v2_router.include_router(reports_router)
v2_router.include_router(activity_router)
v2_router.include_router(knowledge_router)