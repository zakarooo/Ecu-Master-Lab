"""
Connexion PostgreSQL — SQLAlchemy 2.x.

Moteur, session, Base et health-check.
Toute la config vient de .env via config.py.
"""

import logging
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings

logger = logging.getLogger("ecu_engine.database")

# ── Moteur avec pool de connexions ───────────────────────────
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,
)

# ── Session factory ──────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ── Base déclarative SQLAlchemy 2.x ─────────────────────────
class Base(DeclarativeBase):
    pass


# ── Dependency FastAPI ───────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Health-check ─────────────────────────────────────────────
def check_db_connection() -> dict:
    """Teste la connexion et retourne le statut."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        return {"status": "connected", "url": _mask_url(settings.DATABASE_URL)}
    except Exception as e:
        logger.error("Erreur connexion PostgreSQL: %s", e)
        return {"status": "error", "error": str(e)}


def list_tables() -> list:
    """Liste toutes les tables du schéma public."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' ORDER BY table_name"
            ))
            return [row[0] for row in result.fetchall()]
    except Exception as e:
        logger.error("Erreur listing tables: %s", e)
        return []


def _mask_url(url: str) -> str:
    """Masque le mot de passe dans l'URL pour les logs."""
    try:
        at = url.index("@")
        proto_user = url[:url.index(":", url.index("://") + 3)]
        return f"{proto_user}:***@{url[at + 1:]}"
    except Exception:
        return url
