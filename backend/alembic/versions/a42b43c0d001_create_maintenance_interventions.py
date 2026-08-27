"""create maintenance interventions

Revision ID: a42b43c0d001
Revises: 0672cb0ffd6a
Create Date: 2026-08-27
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "a42b43c0d001"
down_revision: str | None = "0672cb0ffd6a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "maintenance_interventions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("machine_id", sa.UUID(), nullable=False),
        sa.Column("machine_type", sa.String(length=100), nullable=True),
        sa.Column("intervention_type", sa.String(length=150), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column(
            "failure_prediction",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "recommendation",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("technician_notes", sa.Text(), nullable=True),
        sa.Column(
            "before_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "after_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "verification_result",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("outcome_label", sa.String(length=40), nullable=True),
        sa.Column("outcome_score", sa.Float(), nullable=True),
        sa.Column(
            "outcome_evidence",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
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
    )

    op.create_index(
        "ix_maintenance_interventions_machine",
        "maintenance_interventions",
        ["machine_id"],
        unique=False,
    )
    op.create_index(
        "ix_maintenance_interventions_type",
        "maintenance_interventions",
        ["intervention_type"],
        unique=False,
    )
    op.create_index(
        "ix_maintenance_interventions_status",
        "maintenance_interventions",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_maintenance_interventions_machine_type",
        "maintenance_interventions",
        ["machine_type"],
        unique=False,
    )
    op.create_index(
        "ix_maintenance_interventions_completed",
        "maintenance_interventions",
        ["completed_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_maintenance_interventions_completed",
        table_name="maintenance_interventions",
    )
    op.drop_index(
        "ix_maintenance_interventions_machine_type",
        table_name="maintenance_interventions",
    )
    op.drop_index(
        "ix_maintenance_interventions_status",
        table_name="maintenance_interventions",
    )
    op.drop_index(
        "ix_maintenance_interventions_type",
        table_name="maintenance_interventions",
    )
    op.drop_index(
        "ix_maintenance_interventions_machine",
        table_name="maintenance_interventions",
    )
    op.drop_table("maintenance_interventions")
