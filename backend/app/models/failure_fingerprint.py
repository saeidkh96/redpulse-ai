import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class FailureFingerprint(Base):
    __tablename__ = "failure_fingerprints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    machine_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "machines.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    failure_type: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    machine_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    baseline_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    trajectory_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    trajectory_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    failure_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    dominant_sensors: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    deviation_signature: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    drift_signature: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    correlation_signature: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    trajectory_summary: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    evidence: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
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
            "ix_failure_fingerprints_machine",
            "machine_id",
        ),
        Index(
            "ix_failure_fingerprints_failure_type",
            "failure_type",
        ),
        Index(
            "ix_failure_fingerprints_machine_type",
            "machine_type",
        ),
        Index(
            "ix_failure_fingerprints_created",
            "created_at",
        ),
    )
