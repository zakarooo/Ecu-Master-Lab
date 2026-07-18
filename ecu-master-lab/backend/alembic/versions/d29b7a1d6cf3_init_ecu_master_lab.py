"""init_ecu_master_lab

Revision ID: d29b7a1d6cf3
Revises: 
Create Date: 2026-07-15 21:51:52.736091

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'd29b7a1d6cf3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tables core — créer seulement si elles n'existent pas
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")

    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            phone VARCHAR(20),
            hashed_password VARCHAR(255) NOT NULL,
            role VARCHAR(20) DEFAULT 'client',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            status VARCHAR(30) DEFAULT 'pending',
            vehicle_make VARCHAR(100),
            vehicle_model VARCHAR(100),
            vehicle_year INTEGER,
            vehicle_engine VARCHAR(100),
            vehicle_power VARCHAR(50),
            vehicle_ecu_type VARCHAR(100),
            vehicle_mileage INTEGER,
            vehicle_gearbox VARCHAR(50),
            vehicle_vin VARCHAR(17),
            tool_used VARCHAR(100),
            ecu_filename VARCHAR(255),
            ecu_file_path VARCHAR(500),
            ecu_file_size INTEGER,
            ecu_file_hash VARCHAR(64),
            ecu_original_backup VARCHAR(500),
            ai_detected_ecu VARCHAR(100),
            ai_detected_hw VARCHAR(100),
            ai_detected_sw VARCHAR(100),
            ai_checksum_valid BOOLEAN,
            ai_confidence DOUBLE PRECISION,
            ai_analysis_json TEXT,
            modifications TEXT,
            client_notes TEXT,
            result_file_path VARCHAR(500),
            result_checksum VARCHAR(64),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS file_versions (
            id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            version_number INTEGER NOT NULL,
            file_path VARCHAR(500) NOT NULL,
            file_hash VARCHAR(64),
            label VARCHAR(50),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            action VARCHAR(100) NOT NULL,
            resource_type VARCHAR(50),
            resource_id INTEGER,
            details TEXT,
            ip_address VARCHAR(45),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    # Index
    op.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_file_versions_project_id ON file_versions(project_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_audit_logs_created_at")
    op.execute("DROP INDEX IF EXISTS idx_audit_logs_user_id")
    op.execute("DROP INDEX IF EXISTS idx_file_versions_project_id")
    op.execute("DROP INDEX IF EXISTS idx_projects_status")
    op.execute("DROP INDEX IF EXISTS idx_projects_user_id")
    op.execute("DROP INDEX IF EXISTS idx_users_email")
    op.drop_table('audit_logs')
    op.drop_table('file_versions')
    op.drop_table('projects')
    op.drop_table('users')
