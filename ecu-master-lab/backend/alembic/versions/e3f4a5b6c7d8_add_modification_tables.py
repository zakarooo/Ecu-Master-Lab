"""Add modification tables for file editing pipeline

Revision ID: e3f4a5b6c7d8
Revises: a1dab0d2fa0c
Create Date: 2026-07-18

"""
from alembic import op
import sqlalchemy as sa


revision = "e3f4a5b6c7d8"
down_revision = "a1dab0d2fa0c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "modification_sessions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ecu_file_id", sa.Integer, sa.ForeignKey("ecu_files.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("session_name", sa.String(200)),
        sa.Column("description", sa.Text),
        sa.Column("status", sa.String(50), default="draft"),
        sa.Column("original_sha256", sa.String(64)),
        sa.Column("modified_sha256", sa.String(64)),
        sa.Column("is_applied", sa.Boolean, default=False),
        sa.Column("applied_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index("ix_modification_sessions_ecu_file_id", "modification_sessions", ["ecu_file_id"])
    op.create_index("ix_modification_sessions_user_id", "modification_sessions", ["user_id"])
    op.create_index("ix_modification_sessions_status", "modification_sessions", ["status"])

    op.create_table(
        "map_edits",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("modification_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("map_name", sa.String(200)),
        sa.Column("map_offset", sa.BigInteger, nullable=False),
        sa.Column("map_size", sa.Integer),
        sa.Column("map_rows", sa.Integer),
        sa.Column("map_cols", sa.Integer),
        sa.Column("data_type", sa.String(20), default="uint16"),
        sa.Column("byte_order", sa.String(20), default="little_endian"),
        sa.Column("original_values", sa.Text),
        sa.Column("modified_values", sa.Text),
        sa.Column("diff_summary", sa.Text),
        sa.Column("values_changed", sa.Integer, default=0),
        sa.Column("conversion_name", sa.String(50)),
        sa.Column("conversion_factor", sa.Float, default=1.0),
        sa.Column("conversion_offset", sa.Float, default=0.0),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_map_edits_session_id", "map_edits", ["session_id"])

    op.create_table(
        "modification_jobs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("modification_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), default="pending"),
        sa.Column("input_params", sa.Text),
        sa.Column("output_result", sa.Text),
        sa.Column("error_message", sa.Text),
        sa.Column("checksum_before", sa.String(50)),
        sa.Column("checksum_after", sa.String(50)),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_modification_jobs_session_id", "modification_jobs", ["session_id"])
    op.create_index("ix_modification_jobs_status", "modification_jobs", ["status"])


def downgrade() -> None:
    op.drop_table("modification_jobs")
    op.drop_table("map_edits")
    op.drop_table("modification_sessions")
