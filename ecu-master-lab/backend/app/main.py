import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.database import engine, Base, check_db_connection, list_tables
from app.routes import auth, projects, admin
from app.routes.v2 import v2_router

import json

logger = logging.getLogger("ecu_engine")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown — vérifie la connexion DB au démarrage."""
    db_status = check_db_connection()
    if db_status["status"] == "connected":
        tables = list_tables()
        logger.info("PostgreSQL connecté: %s", db_status["url"])
        logger.info("Tables trouvées (%d): %s", len(tables), ", ".join(tables))
    else:
        logger.error("PostgreSQL inaccessible: %s", db_status.get("error"))
    logger.info("CORS_ORIGINS: %s", settings.CORS_ORIGINS)

    # Telegram startup notification
    try:
        from app.ecu_engine.telegram_notifier import notify_startup
        notify_startup(settings.APP_NAME, settings.APP_VERSION)
    except Exception:
        pass

    yield
    engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Plateforme SaaS professionnelle d'analyse et modification ECU avec Agent IA",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(admin.router)
app.include_router(v2_router)


@app.get("/")
def root():
    return RedirectResponse(url="/api/health")


@app.get("/api/health")
def health_check():
    db_status = check_db_connection()
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": db_status["status"],
    }


connected_clients: List[WebSocket] = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


async def broadcast_update(project_id: int, status: str, message: str):
    for client in connected_clients:
        try:
            await client.send_json({
                "type": "project_update",
                "project_id": project_id,
                "status": status,
                "message": message,
            })
        except Exception:
            pass
