import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class BehaviorEventType(str, enum.Enum):
    DEVIATION = "deviation"
    DRIFT = "drift"
    RECOVERY = "recovery"
    MAINTENANCE = "maintenance"
    FAILURE = "failure"


class BehaviorSeverity(str, enum.Enum):
    INFO = "info"
    NORMAL = "normal"
    WARNING = "warning"
    ANOMALOUS = "anomalous"
    CRITICAL = "critical"


class BehaviorEvent(Base):
    __tablename__ = "behavior_events"

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

    event_type: Mapped[BehaviorEventType] = mapped_column(
        Enum(
            BehaviorEventType,
            name="behavior_event_type",
            values_callable=lambda enum_cls: [
                item.value
                for item in enum_cls
            ],
        ),
        nullable=False,
    )

    severity: Mapped[BehaviorSeverity] = mapped_column(
        Enum(
            BehaviorSeverity,
            name="behavior_severity",
            values_callable=lambda enum_cls: [
                item.value
                for item in enum_cls
            ],
        ),
        nullable=False,
    )

    score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    baseline_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    window_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    window_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    summary: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
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

    __table_args__ = (
        Index(
            "ix_behavior_events_machine_created",
            "machine_id",
            "created_at",
        ),
        Index(
            "ix_behavior_events_machine_type",
            "machine_id",
            "event_type",
        ),
        Index(
            "ix_behavior_events_severity",
            "severity",
        ),
    )
