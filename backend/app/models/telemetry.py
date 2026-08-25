import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Telemetry(Base):
    __tablename__ = "telemetry"

    machine_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("machines.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
        nullable=False,
        server_default=func.now(),
    )

    sensor: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
        nullable=False,
    )

    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    __table_args__ = (
        Index(
            "ix_telemetry_machine_timestamp",
            "machine_id",
            "timestamp",
        ),
        Index(
            "ix_telemetry_machine_sensor_timestamp",
            "machine_id",
            "sensor",
            "timestamp",
        ),
    )
