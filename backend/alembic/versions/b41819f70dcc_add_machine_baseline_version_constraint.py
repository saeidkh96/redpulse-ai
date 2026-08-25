"""add machine baseline version constraint

Revision ID: b41819f70dcc
Revises: 8904470df3d1
Create Date: 2026-08-25
"""

from collections.abc import Sequence

from alembic import op


revision: str = "b41819f70dcc"
down_revision: str | None = "8904470df3d1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_machine_baselines_machine_version",
        "machine_baselines",
        [
            "machine_id",
            "baseline_version",
        ],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_machine_baselines_machine_version",
        "machine_baselines",
        type_="unique",
    )
