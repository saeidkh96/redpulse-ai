"""create behavioral memory events

Revision ID: 4f053747ab19
Revises: b41819f70dcc
Create Date: 2026-08-26
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "4f053747ab19"
down_revision: str | None = "b41819f70dcc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "behavior_events",
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
            "event_type",
            sa.Enum(
                "deviation",
                "drift",
                "recovery",
                "maintenance",
                "failure",
                name="behavior_event_type",
            ),
            nullable=False,
        ),
        sa.Column(
            "severity",
            sa.Enum(
                "info",
                "normal",
                "warning",
                "anomalous",
                "critical",
                name="behavior_severity",
            ),
            nullable=False,
        ),
        sa.Column(
            "score",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "baseline_version",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "window_start",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "window_end",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "summary",
            sa.String(length=500),
            nullable=True,
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
        sa.ForeignKeyConstraint(
            ["machine_id"],
            ["machines.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_behavior_events_machine_created",
        "behavior_events",
        [
            "machine_id",
            "created_at",
        ],
        unique=False,
    )

    op.create_index(
        "ix_behavior_events_machine_type",
        "behavior_events",
        [
            "machine_id",
            "event_type",
        ],
        unique=False,
    )

    op.create_index(
        "ix_behavior_events_severity",
        "behavior_events",
        [
            "severity",
        ],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_behavior_events_severity",
        table_name="behavior_events",
    )

    op.drop_index(
        "ix_behavior_events_machine_type",
        table_name="behavior_events",
    )

    op.drop_index(
        "ix_behavior_events_machine_created",
        table_name="behavior_events",
    )

    op.drop_table(
        "behavior_events"
    )

    op.execute(
        "DROP TYPE IF EXISTS behavior_severity"
    )

    op.execute(
        "DROP TYPE IF EXISTS behavior_event_type"
    )
