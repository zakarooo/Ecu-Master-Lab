"""add_ecu_files_fk_constraints

Revision ID: f7e8d9c0b1a2
Revises: 6adc349111c0
Create Date: 2026-07-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7e8d9c0b1a2'
down_revision: Union[str, None] = '6adc349111c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_foreign_key(
        'fk_ecu_files_project_id',
        'ecu_files', 'projects',
        ['project_id'], ['id'],
        ondelete='SET NULL',
    )
    op.create_foreign_key(
        'fk_ecu_files_uploaded_by',
        'ecu_files', 'users',
        ['uploaded_by'], ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_ecu_files_uploaded_by', 'ecu_files', type_='foreignkey')
    op.drop_constraint('fk_ecu_files_project_id', 'ecu_files', type_='foreignkey')
