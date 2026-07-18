"""Add knowledge database tables (Phase 2)

Revision ID: c1d2e3f4g5h6
Revises: b1c2d3e4f5a6
Create Date: 2026-07-16

"""
from alembic import op
import sqlalchemy as sa


revision = "c1d2e3f4g5h6"
down_revision = "b1c2d3e4f5a6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "known_ecu_files",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("filename", sa.String(255)),
        sa.Column("file_path", sa.String(500)),
        sa.Column("file_size", sa.BigInteger),
        sa.Column("ecu_model_id", sa.Integer, nullable=True),
        sa.Column("ecu_model_name", sa.String(200)),
        sa.Column("manufacturer_name", sa.String(100)),
        sa.Column("confirmed_by", sa.Integer, nullable=True),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_known_ecu_files_sha256", "known_ecu_files", ["sha256"])
    op.create_index("ix_known_ecu_files_ecu_model_id", "known_ecu_files", ["ecu_model_id"])

    op.create_table(
        "known_signatures",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ecu_model_id", sa.Integer, nullable=True),
        sa.Column("ecu_model_name", sa.String(200)),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("pattern_hex", sa.String(200), nullable=False),
        sa.Column("pattern_bytes", sa.LargeBinary),
        sa.Column("offset_relative", sa.Boolean, default=False),
        sa.Column("context_hex", sa.String(200)),
        sa.Column("occurrence_count", sa.Integer, default=1),
        sa.Column("total_known_files", sa.Integer, default=0),
        sa.Column("confidence", sa.Float, default=0.5),
        sa.Column("source_file_id", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_known_signatures_pattern_hex", "known_signatures", ["pattern_hex"])
    op.create_index("ix_known_signatures_ecu_model_id", "known_signatures", ["ecu_model_id"])
    op.create_index("ix_known_signatures_category", "known_signatures", ["category"])

    op.create_table(
        "known_strings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ecu_model_id", sa.Integer, nullable=True),
        sa.Column("ecu_model_name", sa.String(200)),
        sa.Column("string_value", sa.String(500), nullable=False),
        sa.Column("offset", sa.BigInteger),
        sa.Column("category", sa.String(50)),
        sa.Column("occurrence_count", sa.Integer, default=1),
        sa.Column("total_known_files", sa.Integer, default=0),
        sa.Column("confidence", sa.Float, default=0.5),
        sa.Column("source_file_id", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_known_strings_string_value", "known_strings", ["string_value"])
    op.create_index("ix_known_strings_ecu_model_id", "known_strings", ["ecu_model_id"])
    op.create_index("ix_known_strings_category", "known_strings", ["category"])

    op.create_table(
        "known_maps",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ecu_model_id", sa.Integer, nullable=True),
        sa.Column("ecu_model_name", sa.String(200)),
        sa.Column("map_name", sa.String(200)),
        sa.Column("offset_hex", sa.String(20)),
        sa.Column("offset_dec", sa.BigInteger),
        sa.Column("size_bytes", sa.Integer),
        sa.Column("rows", sa.Integer),
        sa.Column("cols", sa.Integer),
        sa.Column("data_type", sa.String(20)),
        sa.Column("category", sa.String(50)),
        sa.Column("occurrence_count", sa.Integer, default=1),
        sa.Column("total_known_files", sa.Integer, default=0),
        sa.Column("confidence", sa.Float, default=0.5),
        sa.Column("source_file_id", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_known_maps_ecu_model_id", "known_maps", ["ecu_model_id"])

    op.create_table(
        "known_checksums",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ecu_model_id", sa.Integer, nullable=True),
        sa.Column("ecu_model_name", sa.String(200)),
        sa.Column("algorithm", sa.String(50), nullable=False),
        sa.Column("offset", sa.BigInteger),
        sa.Column("size", sa.Integer),
        sa.Column("data_range_start", sa.BigInteger),
        sa.Column("data_range_end", sa.BigInteger),
        sa.Column("occurrence_count", sa.Integer, default=1),
        sa.Column("total_known_files", sa.Integer, default=0),
        sa.Column("confidence", sa.Float, default=0.5),
        sa.Column("source_file_id", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_known_checksums_ecu_model_id", "known_checksums", ["ecu_model_id"])

    op.create_table(
        "known_segments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ecu_model_id", sa.Integer, nullable=True),
        sa.Column("ecu_model_name", sa.String(200)),
        sa.Column("segment_type", sa.String(50)),
        sa.Column("start_offset", sa.BigInteger),
        sa.Column("end_offset", sa.BigInteger),
        sa.Column("entropy", sa.Float),
        sa.Column("occurrence_count", sa.Integer, default=1),
        sa.Column("total_known_files", sa.Integer, default=0),
        sa.Column("confidence", sa.Float, default=0.5),
        sa.Column("source_file_id", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_known_segments_ecu_model_id", "known_segments", ["ecu_model_id"])

    op.create_table(
        "analysis_corrections",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("analysis_id", sa.Integer, sa.ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_prediction", sa.String(200)),
        sa.Column("corrected_model_id", sa.Integer, nullable=True),
        sa.Column("corrected_model_name", sa.String(200)),
        sa.Column("corrected_manufacturer", sa.String(100)),
        sa.Column("comment", sa.Text),
        sa.Column("corrected_by", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_analysis_corrections_analysis_id", "analysis_corrections", ["analysis_id"])


def downgrade() -> None:
    op.drop_table("analysis_corrections")
    op.drop_table("known_segments")
    op.drop_table("known_checksums")
    op.drop_table("known_maps")
    op.drop_table("known_strings")
    op.drop_table("known_signatures")
    op.drop_table("known_ecu_files")
