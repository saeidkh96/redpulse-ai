"""add durable runtime replay executions

Revision ID: e371f044bd60
Revises: a42b43c0d001
Create Date: 2026-09-02 23:15:24.826686

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "e371f044bd60"
down_revision: Union[str, Sequence[str], None] = "a42b43c0d001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "runtime_replay_executions",
        sa.Column(
            "execution_key",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "tenant_id",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "workflow_id",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "stage_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "state",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "attempts",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "value",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "error",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "lease_owner",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "lease_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
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
        sa.PrimaryKeyConstraint("execution_key"),
    )

    op.create_index(
        "ix_runtime_replay_executions_state",
        "runtime_replay_executions",
        ["state"],
        unique=False,
    )
    op.create_index(
        "ix_runtime_replay_executions_tenant",
        "runtime_replay_executions",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "ix_runtime_replay_executions_workflow_stage",
        "runtime_replay_executions",
        ["workflow_id", "stage_name"],
        unique=False,
    )
    op.create_index(
        "ix_runtime_replay_executions_lease_expires_at",
        "runtime_replay_executions",
        ["lease_expires_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_runtime_replay_executions_lease_expires_at",
        table_name="runtime_replay_executions",
    )
    op.drop_index(
        "ix_runtime_replay_executions_workflow_stage",
        table_name="runtime_replay_executions",
    )
    op.drop_index(
        "ix_runtime_replay_executions_tenant",
        table_name="runtime_replay_executions",
    )
    op.drop_index(
        "ix_runtime_replay_executions_state",
        table_name="runtime_replay_executions",
    )

    op.drop_table("runtime_replay_executions")
