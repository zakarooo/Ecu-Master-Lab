"""v2_add_34_ecu_tables

Revision ID: a1b2c3d4e5f6
Revises: d29b7a1d6cf3
Create Date: 2026-07-15 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'd29b7a1d6cf3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =========================================================================
    # Phase 1 - Independent tables (no FKs to other new tables)
    # =========================================================================

    # 1. activity_logs
    op.create_table(
        'activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_activity_logs_user_id', 'activity_logs', ['user_id'])
    op.create_index('ix_activity_logs_action', 'activity_logs', ['action'])
    op.create_index('ix_activity_logs_resource_type', 'activity_logs', ['resource_type'])
    op.create_index('ix_activity_logs_created_at', 'activity_logs', ['created_at'])

    # 2. ai_models
    op.create_table(
        'ai_models',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=True),
        sa.Column('version', sa.String(50), nullable=True),
        sa.Column('model_type', sa.String(50), nullable=True),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('training_date', sa.DateTime(), nullable=True),
        sa.Column('training_samples', sa.Integer(), nullable=True),
        sa.Column('config_json', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )

    # 3. heuristics
    op.create_table(
        'heuristics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('rule_json', sa.Text(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('hit_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )

    # 4. map_categories (self-referential FK on parent_id)
    op.create_table(
        'map_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['parent_id'], ['map_categories.id']),
    )

    # 5. map_units
    op.create_table(
        'map_units',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(20), unique=True, nullable=False),
        sa.Column('name', sa.String(50), nullable=True),
        sa.Column('unit_type', sa.String(30), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )

    # 6. vehicle_brands
    op.create_table(
        'vehicle_brands',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )

    # 7. manufacturers
    op.create_table(
        'manufacturers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )

    # 8. processors
    op.create_table(
        'processors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('family', sa.String(50), nullable=True),
        sa.Column('manufacturer', sa.String(100), nullable=True),
        sa.Column('architecture', sa.String(50), nullable=True),
        sa.Column('word_size', sa.Integer(), nullable=True),
        sa.Column('endianness', sa.String(10), nullable=True),
        sa.Column('clock_mhz', sa.Integer(), nullable=True),
        sa.Column('flash_kb', sa.Integer(), nullable=True),
        sa.Column('ram_kb', sa.Integer(), nullable=True),
        sa.Column('extensions', sa.Text(), nullable=True),
        sa.Column('known_ecus', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )

    # 9. protocols
    op.create_table(
        'protocols',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), unique=True, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('requires_bootloader', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('typical_tools', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )

    # 10. checksum_algorithms
    op.create_table(
        'checksum_algorithms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('manufacturer', sa.String(100), nullable=True),
        sa.Column('polynomial', sa.String(50), nullable=True),
        sa.Column('init_value', sa.String(50), nullable=True),
        sa.Column('xor_out', sa.String(50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )

    # 11. ecu_files (no FKs to new tables - project_id is nullable int, no FK)
    op.create_table(
        'ecu_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('filename', sa.String(255), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('sha256', sa.String(64), nullable=True),
        sa.Column('md5', sa.String(32), nullable=True),
        sa.Column('file_format', sa.String(20), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('uploaded_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ecu_files_sha256', 'ecu_files', ['sha256'])

    # =========================================================================
    # Phase 2 - Tables depending on Phase 1
    # =========================================================================

    # 12. ecu_models (FK -> manufacturers)
    op.create_table(
        'ecu_models',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('manufacturer_id', sa.Integer(), nullable=False),
        sa.Column('model_name', sa.String(100), nullable=False),
        sa.Column('family', sa.String(50), nullable=True),
        sa.Column('processor_type', sa.String(100), nullable=True),
        sa.Column('flash_size_kb', sa.Integer(), nullable=True),
        sa.Column('eeprom_size_kb', sa.Integer(), nullable=True),
        sa.Column('ram_size_kb', sa.Integer(), nullable=True),
        sa.Column('typical_brands', sa.Text(), nullable=True),
        sa.Column('typical_engines', sa.Text(), nullable=True),
        sa.Column('protocol', sa.String(50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['manufacturer_id'], ['manufacturers.id']),
    )
    op.create_index('ix_ecu_models_manufacturer_id', 'ecu_models', ['manufacturer_id'])

    # 13. vehicle_models (FK -> vehicle_brands)
    op.create_table(
        'vehicle_models',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('year_start', sa.Integer(), nullable=True),
        sa.Column('year_end', sa.Integer(), nullable=True),
        sa.Column('body_type', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['brand_id'], ['vehicle_brands.id']),
    )
    op.create_index('ix_vehicle_models_brand_id', 'vehicle_models', ['brand_id'])

    # 14. map_axes (FK -> map_units)
    op.create_table(
        'map_axes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=True),
        sa.Column('axis_type', sa.String(20), nullable=True),
        sa.Column('unit_id', sa.Integer(), nullable=True),
        sa.Column('min_value', sa.Float(), nullable=True),
        sa.Column('max_value', sa.Float(), nullable=True),
        sa.Column('num_points', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['unit_id'], ['map_units.id']),
    )
    op.create_index('ix_map_axes_unit_id', 'map_axes', ['unit_id'])

    # =========================================================================
    # Phase 3 - Tables depending on Phase 2
    # =========================================================================

    # 15. ecu_variants (FK -> ecu_models)
    op.create_table(
        'ecu_variants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ecu_model_id', sa.Integer(), nullable=False),
        sa.Column('variant_name', sa.String(100), nullable=True),
        sa.Column('hw_revision', sa.String(50), nullable=True),
        sa.Column('sw_revision', sa.String(50), nullable=True),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('checksum_type', sa.String(50), nullable=True),
        sa.Column('is_encrypted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ecu_model_id'], ['ecu_models.id']),
    )
    op.create_index('ix_ecu_variants_ecu_model_id', 'ecu_variants', ['ecu_model_id'])

    # 16. vehicle_engines (FK -> vehicle_models, ecu_models)
    op.create_table(
        'vehicle_engines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model_id', sa.Integer(), nullable=False),
        sa.Column('engine_code', sa.String(50), nullable=True),
        sa.Column('displacement_cc', sa.Integer(), nullable=True),
        sa.Column('fuel_type', sa.String(30), nullable=True),
        sa.Column('power_hp', sa.Integer(), nullable=True),
        sa.Column('torque_nm', sa.Integer(), nullable=True),
        sa.Column('emission_standard', sa.String(30), nullable=True),
        sa.Column('ecu_model_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['model_id'], ['vehicle_models.id']),
        sa.ForeignKeyConstraint(['ecu_model_id'], ['ecu_models.id']),
    )
    op.create_index('ix_vehicle_engines_model_id', 'vehicle_engines', ['model_id'])
    op.create_index('ix_vehicle_engines_ecu_model_id', 'vehicle_engines', ['ecu_model_id'])

    # 17. software_versions (FK -> ecu_models)
    op.create_table(
        'software_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ecu_model_id', sa.Integer(), nullable=False),
        sa.Column('sw_number', sa.String(100), nullable=True),
        sa.Column('hw_number', sa.String(100), nullable=True),
        sa.Column('calibration_id', sa.String(100), nullable=True),
        sa.Column('cvn', sa.String(100), nullable=True),
        sa.Column('version_label', sa.String(100), nullable=True),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('checksum_value', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ecu_model_id'], ['ecu_models.id']),
        sa.UniqueConstraint('ecu_model_id', 'sw_number', name='uq_sw_version_model_sw'),
    )
    op.create_index('ix_software_versions_ecu_model_id', 'software_versions', ['ecu_model_id'])
    op.create_index('ix_software_versions_sw_number', 'software_versions', ['sw_number'])

    # 18. hardware_versions (FK -> ecu_models, processors)
    op.create_table(
        'hardware_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ecu_model_id', sa.Integer(), nullable=False),
        sa.Column('hw_number', sa.String(100), nullable=True),
        sa.Column('revision', sa.String(50), nullable=True),
        sa.Column('board_type', sa.String(50), nullable=True),
        sa.Column('processor_id', sa.Integer(), nullable=True),
        sa.Column('flash_size_kb', sa.Integer(), nullable=True),
        sa.Column('eeprom_size_kb', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ecu_model_id'], ['ecu_models.id']),
        sa.ForeignKeyConstraint(['processor_id'], ['processors.id']),
    )
    op.create_index('ix_hardware_versions_ecu_model_id', 'hardware_versions', ['ecu_model_id'])
    op.create_index('ix_hardware_versions_hw_number', 'hardware_versions', ['hw_number'])
    op.create_index('ix_hardware_versions_processor_id', 'hardware_versions', ['processor_id'])

    # 19. memory_layouts (FK -> ecu_models)
    op.create_table(
        'memory_layouts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ecu_model_id', sa.Integer(), nullable=False),
        sa.Column('total_size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('address_bus_width', sa.Integer(), nullable=True),
        sa.Column('data_bus_width', sa.Integer(), nullable=True),
        sa.Column('endianness', sa.String(10), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ecu_model_id'], ['ecu_models.id']),
    )
    op.create_index('ix_memory_layouts_ecu_model_id', 'memory_layouts', ['ecu_model_id'])

    # 20. memory_segments (FK -> memory_layouts)
    op.create_table(
        'memory_segments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('layout_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=True),
        sa.Column('segment_type', sa.String(50), nullable=True),
        sa.Column('start_address', sa.BigInteger(), nullable=True),
        sa.Column('end_address', sa.BigInteger(), nullable=True),
        sa.Column('size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('permissions', sa.String(10), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['layout_id'], ['memory_layouts.id']),
    )
    op.create_index('ix_memory_segments_layout_id', 'memory_segments', ['layout_id'])

    # 21. ecu_signatures (FK -> ecu_models)
    op.create_table(
        'ecu_signatures',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ecu_model_id', sa.Integer(), nullable=False),
        sa.Column('signature_name', sa.String(200), nullable=True),
        sa.Column('pattern_hex', sa.Text(), nullable=True),
        sa.Column('offset_hex', sa.String(50), nullable=True),
        sa.Column('offset_dec', sa.BigInteger(), nullable=True),
        sa.Column('confidence_weight', sa.Numeric(5, 2), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ecu_model_id'], ['ecu_models.id']),
    )
    op.create_index('ix_ecu_signatures_ecu_model_id', 'ecu_signatures', ['ecu_model_id'])
    op.create_index('ix_ecu_signatures_confidence', 'ecu_signatures', ['confidence_weight'])

    # 21. binary_patterns (FK -> ecu_models)
    op.create_table(
        'binary_patterns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ecu_model_id', sa.Integer(), nullable=False),
        sa.Column('pattern_name', sa.String(100), nullable=True),
        sa.Column('pattern_hex', sa.Text(), nullable=True),
        sa.Column('offset_start', sa.BigInteger(), nullable=True),
        sa.Column('offset_end', sa.BigInteger(), nullable=True),
        sa.Column('byte_length', sa.Integer(), nullable=True),
        sa.Column('match_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ecu_model_id'], ['ecu_models.id']),
    )
    op.create_index('ix_binary_patterns_ecu_model_id', 'binary_patterns', ['ecu_model_id'])

    # 22. maps (FK -> ecu_models, map_categories, map_units, map_axes)
    op.create_table(
        'maps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ecu_model_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(100), nullable=True),
        sa.Column('address_hex', sa.String(50), nullable=True),
        sa.Column('address_dec', sa.BigInteger(), nullable=True),
        sa.Column('size_bytes', sa.Integer(), nullable=True),
        sa.Column('rows', sa.Integer(), nullable=True),
        sa.Column('cols', sa.Integer(), nullable=True),
        sa.Column('data_type', sa.String(20), nullable=True),
        sa.Column('unit_id', sa.Integer(), nullable=True),
        sa.Column('axis_x_id', sa.Integer(), nullable=True),
        sa.Column('axis_y_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ecu_model_id'], ['ecu_models.id']),
        sa.ForeignKeyConstraint(['category_id'], ['map_categories.id']),
        sa.ForeignKeyConstraint(['unit_id'], ['map_units.id']),
        sa.ForeignKeyConstraint(['axis_x_id'], ['map_axes.id']),
        sa.ForeignKeyConstraint(['axis_y_id'], ['map_axes.id']),
    )
    op.create_index('ix_maps_ecu_model_id', 'maps', ['ecu_model_id'])
    op.create_index('ix_maps_category_id', 'maps', ['category_id'])
    op.create_index('ix_maps_unit_id', 'maps', ['unit_id'])
    op.create_index('ix_maps_axis_x_id', 'maps', ['axis_x_id'])
    op.create_index('ix_maps_axis_y_id', 'maps', ['axis_y_id'])

    # =========================================================================
    # Phase 4 - Tables depending on ecu_files + Phase 2/3
    # =========================================================================

    # 23. analyses (FK -> ecu_files)
    op.create_table(
        'analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ecu_file_id', sa.Integer(), nullable=False),
        sa.Column('detected_manufacturer', sa.String(100), nullable=True),
        sa.Column('detected_ecu_model', sa.String(100), nullable=True),
        sa.Column('detected_ecu_family', sa.String(50), nullable=True),
        sa.Column('detected_processor', sa.String(100), nullable=True),
        sa.Column('detected_protocol', sa.String(50), nullable=True),
        sa.Column('detected_hw_version', sa.String(100), nullable=True),
        sa.Column('detected_sw_version', sa.String(100), nullable=True),
        sa.Column('detected_brand', sa.String(100), nullable=True),
        sa.Column('detected_engine', sa.String(100), nullable=True),
        sa.Column('confidence', sa.Numeric(5, 2), nullable=True),
        sa.Column('consistency_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('needs_review', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('review_reasons', sa.Text(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('engine_version', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ecu_file_id'], ['ecu_files.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_analyses_ecu_file_id', 'analyses', ['ecu_file_id'])
    op.create_index('ix_analyses_confidence', 'analyses', ['confidence'])
    op.create_index('ix_analyses_created_at', 'analyses', ['created_at'])

    # 24. learning_datasets (FK -> ecu_files)
    op.create_table(
        'learning_datasets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ecu_file_id', sa.Integer(), nullable=False),
        sa.Column('label_manufacturer', sa.String(100), nullable=True),
        sa.Column('label_ecu_model', sa.String(100), nullable=True),
        sa.Column('label_processor', sa.String(100), nullable=True),
        sa.Column('is_validated', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('validated_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ecu_file_id'], ['ecu_files.id']),
    )
    op.create_index('ix_learning_datasets_ecu_file_id', 'learning_datasets', ['ecu_file_id'])

    # =========================================================================
    # Phase 5 - Tables depending on analyses
    # =========================================================================

    # 25. analysis_results (FK -> analyses)
    op.create_table(
        'analysis_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.Integer(), nullable=False),
        sa.Column('result_type', sa.String(50), nullable=True),
        sa.Column('result_data', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Numeric(5, 2), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_analysis_results_analysis_id', 'analysis_results', ['analysis_id'])
    op.create_index('ix_analysis_results_analysis_type', 'analysis_results', ['analysis_id', 'result_type'])

    # 26. analysis_hypotheses (FK -> analyses, ecu_models)
    op.create_table(
        'analysis_hypotheses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.Integer(), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('ecu_model_id', sa.Integer(), nullable=True),
        sa.Column('ecu_name', sa.String(100), nullable=True),
        sa.Column('probability', sa.Numeric(5, 2), nullable=True),
        sa.Column('evidence', sa.Text(), nullable=True),
        sa.Column('is_rejected', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('rejection_reasons', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ecu_model_id'], ['ecu_models.id']),
    )
    op.create_index('ix_analysis_hypotheses_analysis_id', 'analysis_hypotheses', ['analysis_id'])
    op.create_index('ix_analysis_hypotheses_ecu_model_id', 'analysis_hypotheses', ['ecu_model_id'])

    # 27. analysis_scores (FK -> analyses)
    op.create_table(
        'analysis_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.Integer(), nullable=False),
        sa.Column('factor', sa.String(100), nullable=True),
        sa.Column('raw_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('weight', sa.Numeric(5, 2), nullable=True),
        sa.Column('weighted_score', sa.Numeric(7, 2), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_analysis_scores_analysis_id', 'analysis_scores', ['analysis_id'])

    # 28. detected_maps (FK -> analyses, maps)
    op.create_table(
        'detected_maps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.Integer(), nullable=False),
        sa.Column('map_id', sa.Integer(), nullable=True),
        sa.Column('map_name', sa.String(100), nullable=True),
        sa.Column('offset_hex', sa.String(50), nullable=True),
        sa.Column('offset_dec', sa.BigInteger(), nullable=True),
        sa.Column('size_bytes', sa.Integer(), nullable=True),
        sa.Column('rows', sa.Integer(), nullable=True),
        sa.Column('cols', sa.Integer(), nullable=True),
        sa.Column('data_type', sa.String(20), nullable=True),
        sa.Column('min_value', sa.Float(), nullable=True),
        sa.Column('max_value', sa.Float(), nullable=True),
        sa.Column('avg_value', sa.Float(), nullable=True),
        sa.Column('entropy', sa.Float(), nullable=True),
        sa.Column('non_empty_ratio', sa.Float(), nullable=True),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('detection_method', sa.String(50), nullable=True),
        sa.Column('confidence', sa.Numeric(5, 2), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['map_id'], ['maps.id']),
    )
    op.create_index('ix_detected_maps_analysis_id', 'detected_maps', ['analysis_id'])
    op.create_index('ix_detected_maps_map_id', 'detected_maps', ['map_id'])

    # 29. detected_segments (FK -> analyses)
    op.create_table(
        'detected_segments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.Integer(), nullable=False),
        sa.Column('segment_type', sa.String(50), nullable=True),
        sa.Column('start_offset', sa.BigInteger(), nullable=True),
        sa.Column('end_offset', sa.BigInteger(), nullable=True),
        sa.Column('size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('entropy', sa.Float(), nullable=True),
        sa.Column('non_empty_ratio', sa.Float(), nullable=True),
        sa.Column('is_valid', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_detected_segments_analysis_id', 'detected_segments', ['analysis_id'])

    # 30. checksum_results (FK -> analyses)
    op.create_table(
        'checksum_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.Integer(), nullable=False),
        sa.Column('algorithm', sa.String(100), nullable=True),
        sa.Column('offset', sa.BigInteger(), nullable=True),
        sa.Column('size', sa.Integer(), nullable=True),
        sa.Column('stored_value', sa.String(100), nullable=True),
        sa.Column('computed_value', sa.String(100), nullable=True),
        sa.Column('is_valid', sa.Boolean(), nullable=True),
        sa.Column('data_start', sa.BigInteger(), nullable=True),
        sa.Column('data_end', sa.BigInteger(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_checksum_results_analysis_id', 'checksum_results', ['analysis_id'])

    # 31. ai_predictions (FK -> analyses, ai_models)
    op.create_table(
        'ai_predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.Integer(), nullable=False),
        sa.Column('model_id', sa.Integer(), nullable=False),
        sa.Column('prediction_type', sa.String(50), nullable=True),
        sa.Column('predicted_value', sa.String(200), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('features_used', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['model_id'], ['ai_models.id']),
    )
    op.create_index('ix_ai_predictions_analysis_id', 'ai_predictions', ['analysis_id'])
    op.create_index('ix_ai_predictions_model_id', 'ai_predictions', ['model_id'])

    # 32. reports (FK -> analyses)
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=True),
        sa.Column('format', sa.String(20), nullable=True),
        sa.Column('content_json', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('generated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_reports_analysis_id', 'reports', ['analysis_id'])

    # =========================================================================
    # Phase 6 - Tables depending on reports
    # =========================================================================

    # 33. exports (FK -> reports)
    op.create_table(
        'exports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.Integer(), nullable=False),
        sa.Column('export_format', sa.String(20), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['report_id'], ['reports.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_exports_report_id', 'exports', ['report_id'])


def downgrade() -> None:
    # =========================================================================
    # Drop in REVERSE order (respect FK dependencies)
    # =========================================================================

    # Phase 6
    op.drop_index('ix_exports_report_id', table_name='exports')
    op.drop_table('exports')

    # Phase 5
    op.drop_index('ix_reports_analysis_id', table_name='reports')
    op.drop_table('reports')

    op.drop_index('ix_ai_predictions_model_id', table_name='ai_predictions')
    op.drop_index('ix_ai_predictions_analysis_id', table_name='ai_predictions')
    op.drop_table('ai_predictions')

    op.drop_index('ix_checksum_results_analysis_id', table_name='checksum_results')
    op.drop_table('checksum_results')

    op.drop_index('ix_detected_segments_analysis_id', table_name='detected_segments')
    op.drop_table('detected_segments')

    op.drop_index('ix_detected_maps_map_id', table_name='detected_maps')
    op.drop_index('ix_detected_maps_analysis_id', table_name='detected_maps')
    op.drop_table('detected_maps')

    op.drop_index('ix_analysis_scores_analysis_id', table_name='analysis_scores')
    op.drop_table('analysis_scores')

    op.drop_index('ix_analysis_hypotheses_ecu_model_id', table_name='analysis_hypotheses')
    op.drop_index('ix_analysis_hypotheses_analysis_id', table_name='analysis_hypotheses')
    op.drop_table('analysis_hypotheses')

    op.drop_index('ix_analysis_results_analysis_type', table_name='analysis_results')
    op.drop_index('ix_analysis_results_analysis_id', table_name='analysis_results')
    op.drop_table('analysis_results')

    # Phase 4
    op.drop_index('ix_learning_datasets_ecu_file_id', table_name='learning_datasets')
    op.drop_table('learning_datasets')

    op.drop_index('ix_analyses_created_at', table_name='analyses')
    op.drop_index('ix_analyses_confidence', table_name='analyses')
    op.drop_index('ix_analyses_ecu_file_id', table_name='analyses')
    op.drop_table('analyses')

    # Phase 3
    op.drop_index('ix_maps_axis_y_id', table_name='maps')
    op.drop_index('ix_maps_axis_x_id', table_name='maps')
    op.drop_index('ix_maps_unit_id', table_name='maps')
    op.drop_index('ix_maps_category_id', table_name='maps')
    op.drop_index('ix_maps_ecu_model_id', table_name='maps')
    op.drop_table('maps')

    op.drop_index('ix_binary_patterns_ecu_model_id', table_name='binary_patterns')
    op.drop_table('binary_patterns')

    op.drop_index('ix_ecu_signatures_confidence', table_name='ecu_signatures')
    op.drop_index('ix_ecu_signatures_ecu_model_id', table_name='ecu_signatures')
    op.drop_table('ecu_signatures')

    op.drop_index('ix_memory_segments_layout_id', table_name='memory_segments')
    op.drop_table('memory_segments')

    op.drop_index('ix_memory_layouts_ecu_model_id', table_name='memory_layouts')
    op.drop_table('memory_layouts')

    op.drop_index('ix_hardware_versions_processor_id', table_name='hardware_versions')
    op.drop_index('ix_hardware_versions_hw_number', table_name='hardware_versions')
    op.drop_index('ix_hardware_versions_ecu_model_id', table_name='hardware_versions')
    op.drop_table('hardware_versions')

    op.drop_index('ix_software_versions_sw_number', table_name='software_versions')
    op.drop_index('ix_software_versions_ecu_model_id', table_name='software_versions')
    op.drop_table('software_versions')

    op.drop_index('ix_vehicle_engines_ecu_model_id', table_name='vehicle_engines')
    op.drop_index('ix_vehicle_engines_model_id', table_name='vehicle_engines')
    op.drop_table('vehicle_engines')

    op.drop_index('ix_ecu_variants_ecu_model_id', table_name='ecu_variants')
    op.drop_table('ecu_variants')

    # Phase 2
    op.drop_index('ix_map_axes_unit_id', table_name='map_axes')
    op.drop_table('map_axes')

    op.drop_index('ix_vehicle_models_brand_id', table_name='vehicle_models')
    op.drop_table('vehicle_models')

    op.drop_index('ix_ecu_models_manufacturer_id', table_name='ecu_models')
    op.drop_table('ecu_models')

    # Phase 1
    op.drop_index('ix_ecu_files_sha256', table_name='ecu_files')
    op.drop_table('ecu_files')

    op.drop_table('checksum_algorithms')
    op.drop_table('protocols')
    op.drop_table('processors')
    op.drop_table('manufacturers')
    op.drop_table('vehicle_brands')
    op.drop_table('map_units')
    op.drop_table('map_categories')

    op.drop_table('heuristics')
    op.drop_table('ai_models')

    op.drop_index('ix_activity_logs_created_at', table_name='activity_logs')
    op.drop_index('ix_activity_logs_resource_type', table_name='activity_logs')
    op.drop_index('ix_activity_logs_action', table_name='activity_logs')
    op.drop_index('ix_activity_logs_user_id', table_name='activity_logs')
    op.drop_table('activity_logs')
