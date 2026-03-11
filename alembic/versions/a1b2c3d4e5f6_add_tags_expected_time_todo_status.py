"""add tags, expected_duration_minutes, and TODO habit status

Revision ID: a1b2c3d4e5f6
Revises: 5930e0d654eb
Create Date: 2026-03-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '5930e0d654eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add TODO to habit_status enum (cannot be rolled back in Postgres)
    op.execute("ALTER TYPE habit_status ADD VALUE IF NOT EXISTS 'TODO' BEFORE 'ACTIVE'")

    # Add new columns to tasks
    op.add_column('tasks', sa.Column('expected_duration_minutes', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('tags', ARRAY(sa.String()), nullable=False, server_default='{}'))

    # Add new columns to habits
    op.add_column('habits', sa.Column('expected_duration_minutes', sa.Integer(), nullable=True))
    op.add_column('habits', sa.Column('tags', ARRAY(sa.String()), nullable=False, server_default='{}'))


def downgrade() -> None:
    op.drop_column('habits', 'tags')
    op.drop_column('habits', 'expected_duration_minutes')
    op.drop_column('tasks', 'tags')
    op.drop_column('tasks', 'expected_duration_minutes')
    # NOTE: PostgreSQL does not support DROP VALUE from an enum type.
    # The 'TODO' value will remain in habit_status after downgrade.
