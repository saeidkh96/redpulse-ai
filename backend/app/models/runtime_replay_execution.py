from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RuntimeReplayExecution(Base):
    __tablename__ = "runtime_replay_executions"

    execution_key: Mapped[str] = mapped_column(String(255), primary_key=True)

    tenant_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    workflow_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    stage_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    state: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    value: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    lease_owner: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    lease_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index(
            "ix_runtime_replay_executions_tenant",
            "tenant_id",
        ),
        Index(
            "ix_runtime_replay_executions_workflow_stage",
            "workflow_id",
            "stage_name",
        ),
        Index(
            "ix_runtime_replay_executions_state",
            "state",
        ),
        Index(
            "ix_runtime_replay_executions_lease_expires_at",
            "lease_expires_at",
        ),
    )
