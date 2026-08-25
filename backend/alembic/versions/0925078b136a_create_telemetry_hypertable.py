"""create telemetry hypertable

Revision ID: 0925078b136a
Revises: fef2fbdda8d5
Create Date: 2026-08-25
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0925078b136a"
down_revision: str | None = "fef2fbdda8d5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "telemetry",
        sa.Column("machine_id", sa.UUID(), nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("sensor", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(
            ["machine_id"],
            ["machines.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "machine_id",
            "timestamp",
            "sensor",
        ),
    )

    op.create_index(
        "ix_telemetry_machine_sensor_timestamp",
        "telemetry",
        ["machine_id", "sensor", "timestamp"],
        unique=False,
    )

    op.create_index(
        "ix_telemetry_machine_timestamp",
        "telemetry",
        ["machine_id", "timestamp"],
        unique=False,
    )

    op.execute(
        """
        SELECT create_hypertable(
            'telemetry',
            'timestamp',
            if_not_exists => TRUE,
            migrate_data => TRUE
        )
        """
    )


def downgrade() -> None:
    op.drop_index(
        "ix_telemetry_machine_timestamp",
        table_name="telemetry",
    )

    op.drop_index(
        "ix_telemetry_machine_sensor_timestamp",
        table_name="telemetry",
    )

    op.drop_table("telemetry")
