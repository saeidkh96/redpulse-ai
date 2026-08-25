"""create machine registry

Revision ID: fef2fbdda8d5
Revises: 74a1b50307cd
Create Date: 2026-08-25
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "fef2fbdda8d5"
down_revision: str | None = "74a1b50307cd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


machine_status = postgresql.ENUM(
    "active",
    "inactive",
    "maintenance",
    "decommissioned",
    name="machine_status",
    create_type=False,
)


def upgrade() -> None:
    machine_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "machines",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("machine_code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("manufacturer", sa.String(length=255), nullable=True),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("machine_type", sa.String(length=100), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("installation_date", sa.Date(), nullable=True),
        sa.Column(
            "status",
            machine_status,
            server_default="active",
            nullable=False,
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
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
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_machines_machine_code"),
        "machines",
        ["machine_code"],
        unique=True,
    )

    op.create_index(
        op.f("ix_machines_machine_type"),
        "machines",
        ["machine_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_machines_status"),
        "machines",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_machines_status"), table_name="machines")
    op.drop_index(op.f("ix_machines_machine_type"), table_name="machines")
    op.drop_index(op.f("ix_machines_machine_code"), table_name="machines")
    op.drop_table("machines")

    machine_status.drop(op.get_bind(), checkfirst=True)
