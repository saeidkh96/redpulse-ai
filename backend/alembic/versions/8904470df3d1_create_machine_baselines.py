"""create machine baselines

Revision ID: 8904470df3d1
Revises: 0925078b136a
Create Date: 2026-08-25
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "8904470df3d1"
down_revision: str | None = "0925078b136a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "machine_baselines",
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "machine_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "baseline_version",
            sa.String(length=50),
            server_default="1",
            nullable=False,
        ),
        sa.Column(
            "sample_count",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "window_start",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "window_end",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "sensor_features",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "correlations",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["machine_id"],
            ["machines.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "sample_count > 0",
            name="ck_machine_baselines_sample_count_positive",
        ),
        sa.CheckConstraint(
            "window_end >= window_start",
            name="ck_machine_baselines_valid_window",
        ),
    )

    op.create_index(
        "ix_machine_baselines_machine_id",
        "machine_baselines",
        ["machine_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_machine_baselines_machine_id",
        table_name="machine_baselines",
    )

    op.drop_table("machine_baselines")
