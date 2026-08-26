"""create failure fingerprint library

Revision ID: 0672cb0ffd6a
Revises: 4f053747ab19
Create Date: 2026-08-26
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0672cb0ffd6a"
down_revision: str | None = "4f053747ab19"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "failure_fingerprints",
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
            "failure_type",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "machine_type",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "confidence",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "baseline_version",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "trajectory_start",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "trajectory_end",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "failure_time",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "dominant_sensors",
            postgresql.JSONB(
                astext_type=sa.Text()
            ),
            nullable=False,
        ),
        sa.Column(
            "deviation_signature",
            postgresql.JSONB(
                astext_type=sa.Text()
            ),
            nullable=False,
        ),
        sa.Column(
            "drift_signature",
            postgresql.JSONB(
                astext_type=sa.Text()
            ),
            nullable=False,
        ),
        sa.Column(
            "correlation_signature",
            postgresql.JSONB(
                astext_type=sa.Text()
            ),
            nullable=False,
        ),
        sa.Column(
            "trajectory_summary",
            postgresql.JSONB(
                astext_type=sa.Text()
            ),
            nullable=False,
        ),
        sa.Column(
            "evidence",
            postgresql.JSONB(
                astext_type=sa.Text()
            ),
            nullable=False,
        ),
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
        "ix_failure_fingerprints_created",
        "failure_fingerprints",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        "ix_failure_fingerprints_failure_type",
        "failure_fingerprints",
        ["failure_type"],
        unique=False,
    )

    op.create_index(
        "ix_failure_fingerprints_machine",
        "failure_fingerprints",
        ["machine_id"],
        unique=False,
    )

    op.create_index(
        "ix_failure_fingerprints_machine_type",
        "failure_fingerprints",
        ["machine_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_failure_fingerprints_machine_type",
        table_name="failure_fingerprints",
    )

    op.drop_index(
        "ix_failure_fingerprints_machine",
        table_name="failure_fingerprints",
    )

    op.drop_index(
        "ix_failure_fingerprints_failure_type",
        table_name="failure_fingerprints",
    )

    op.drop_index(
        "ix_failure_fingerprints_created",
        table_name="failure_fingerprints",
    )

    op.drop_table(
        "failure_fingerprints"
    )
