"""make audit_logs.user_id nullable for anonymous login attempts

Revision ID: a1dab0d2fa0c
Revises: 6adc349111c0
Create Date: 2026-07-17 17:25:39.968909

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1dab0d2fa0c'
down_revision: Union[str, None] = '6adc349111c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('audit_logs', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=True)


def downgrade() -> None:
    op.alter_column('audit_logs', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=False)
