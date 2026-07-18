"""Add composite indexes for ECU V2 table performance

Revision ID: b1c2d3e4f5a6
Revises: a1b2c3d4e5f6
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "b1c2d3e4f5a6"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Analysis queries: find analyses by file
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_analyses_ecu_file "
        "ON analyses (ecu_file_id, created_at DESC)"
    ))

    # Hypotheses by analysis (ranked by probability)
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_hypotheses_analysis_prob "
        "ON analysis_hypotheses (analysis_id, probability DESC)"
    ))

    # Scores by analysis
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_scores_analysis_factor "
        "ON analysis_scores (analysis_id, factor)"
    ))

    # Detected maps by analysis
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_detected_maps_analysis "
        "ON detected_maps (analysis_id, map_name)"
    ))

    # Detected segments by analysis
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_detected_segments_analysis "
        "ON detected_segments (analysis_id, segment_type)"
    ))

    # Checksum results by analysis
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_checksum_results_analysis "
        "ON checksum_results (analysis_id, algorithm)"
    ))

    # Signatures lookup by ECU model
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_ecu_signatures_model "
        "ON ecu_signatures (ecu_model_id, signature_name)"
    ))

    # Binary patterns by ECU model
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_binary_patterns_model "
        "ON binary_patterns (ecu_model_id, pattern_name)"
    ))

    # Memory layouts by ECU model
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_memory_layouts_model "
        "ON memory_layouts (ecu_model_id)"
    ))

    # Memory segments by layout
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_memory_segments_layout "
        "ON memory_segments (layout_id, segment_type)"
    ))

    # Maps lookup by category and unit
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_maps_category_unit "
        "ON maps (category_id, unit_id)"
    ))

    # Maps by ECU model
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_maps_model "
        "ON maps (ecu_model_id)"
    ))

    # ECU models by manufacturer
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_ecu_models_manufacturer "
        "ON ecu_models (manufacturer_id, model_name)"
    ))

    # Software versions by model
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_software_versions_model "
        "ON software_versions (ecu_model_id, sw_number)"
    ))

    # ECU variants by model
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_ecu_variants_model "
        "ON ecu_variants (ecu_model_id, variant_name)"
    ))

    # Activity logs
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_activity_logs_user "
        "ON activity_logs (user_id, created_at DESC)"
    ))
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_activity_logs_resource "
        "ON activity_logs (resource_type, resource_id)"
    ))

    # Vehicle models by brand
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_vehicle_models_brand "
        "ON vehicle_models (brand_id, name)"
    ))

    # Vehicle engines by model
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_vehicle_engines_model "
        "ON vehicle_engines (model_id, engine_code)"
    ))

    # AI predictions by model+analysis
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_ai_predictions_model "
        "ON ai_predictions (model_id, analysis_id)"
    ))

    # Analysis results
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_analysis_results_type "
        "ON analysis_results (analysis_id, result_type)"
    ))

    # Reports by analysis
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_reports_analysis "
        "ON reports (analysis_id, format)"
    ))

    # ECU files by project
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_ecu_files_project "
        "ON ecu_files (project_id)"
    ))
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_ecu_files_sha256 "
        "ON ecu_files (sha256)"
    ))


def downgrade() -> None:
    op.execute(text("DROP INDEX IF EXISTS idx_ecu_files_sha256"))
    op.execute(text("DROP INDEX IF EXISTS idx_ecu_files_project"))
    op.execute(text("DROP INDEX IF EXISTS idx_reports_analysis"))
    op.execute(text("DROP INDEX IF EXISTS idx_analysis_results_type"))
    op.execute(text("DROP INDEX IF EXISTS idx_ai_predictions_model"))
    op.execute(text("DROP INDEX IF EXISTS idx_vehicle_engines_model"))
    op.execute(text("DROP INDEX IF EXISTS idx_vehicle_models_brand"))
    op.execute(text("DROP INDEX IF EXISTS idx_activity_logs_resource"))
    op.execute(text("DROP INDEX IF EXISTS idx_activity_logs_user"))
    op.execute(text("DROP INDEX IF EXISTS idx_ecu_variants_model"))
    op.execute(text("DROP INDEX IF EXISTS idx_software_versions_model"))
    op.execute(text("DROP INDEX IF EXISTS idx_ecu_models_manufacturer"))
    op.execute(text("DROP INDEX IF EXISTS idx_maps_model"))
    op.execute(text("DROP INDEX IF EXISTS idx_maps_category_unit"))
    op.execute(text("DROP INDEX IF EXISTS idx_memory_segments_layout"))
    op.execute(text("DROP INDEX IF EXISTS idx_memory_layouts_model"))
    op.execute(text("DROP INDEX IF EXISTS idx_binary_patterns_model"))
    op.execute(text("DROP INDEX IF EXISTS idx_ecu_signatures_model"))
    op.execute(text("DROP INDEX IF EXISTS idx_checksum_results_analysis"))
    op.execute(text("DROP INDEX IF EXISTS idx_detected_segments_analysis"))
    op.execute(text("DROP INDEX IF EXISTS idx_detected_maps_analysis"))
    op.execute(text("DROP INDEX IF EXISTS idx_scores_analysis_factor"))
    op.execute(text("DROP INDEX IF EXISTS idx_hypotheses_analysis_prob"))
    op.execute(text("DROP INDEX IF EXISTS idx_analyses_ecu_file"))
