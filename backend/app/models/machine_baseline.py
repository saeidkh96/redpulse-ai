import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MachineBaseline(Base):
    __tablename__ = "machine_baselines"

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

    baseline_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="1",
        server_default="1",
    )

    sample_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    window_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    window_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    sensor_features: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    correlations: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "sample_count > 0",
            name="ck_machine_baselines_sample_count_positive",
        ),
        CheckConstraint(
            "window_end >= window_start",
            name="ck_machine_baselines_valid_window",
        ),
        UniqueConstraint(
            "machine_id",
            "baseline_version",
            name="uq_machine_baselines_machine_version",
        ),
        Index(
            "ix_machine_baselines_machine_id",
            "machine_id",
        ),
    )
