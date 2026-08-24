"""enable timescaledb extension

Revision ID: 74a1b50307cd
Revises:
Create Date: 2026-08-25
"""

from collections.abc import Sequence

from alembic import op


revision: str = "74a1b50307cd"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS timescaledb")
