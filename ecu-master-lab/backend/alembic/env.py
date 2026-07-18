"""
Alembic env.py — configuration des migrations.

Lit la DATABASE_URL depuis .env et utilise les modèles SQLAlchemy
pour générer les migrations automatiquement.
"""

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Ajouter le répertoire backend au path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.core.database import Base

# Importer TOUS les modèles pour que Alembic les détecte
from app.models.models import User, Project, FileVersion, AuditLog  # noqa: F401
from app.models.new.ecu_models import (  # noqa: F401
    Manufacturer, ECUModel, ECUVariant, Processor, Protocol, ChecksumAlgorithm,
    VehicleBrand, VehicleModel, VehicleEngine,
    SoftwareVersion, HardwareVersion,
    MemoryLayout, MemorySegment,
    ECUSignature, BinaryPattern,
    MapCategory, MapUnit, MapAxis, Map,
    ECUFile, Analysis, AnalysisResult, AnalysisHypothesis, AnalysisScore,
    DetectedMap, DetectedSegment, ChecksumResult,
    AIModel, AIPrediction, LearningDataset, Heuristic,
    Report, Export, ActivityLog,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Override l'URL depuis .env
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
