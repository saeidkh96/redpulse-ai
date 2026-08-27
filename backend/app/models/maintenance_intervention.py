import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MaintenanceInterventionStatus(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MaintenanceOutcomeLabel(str, enum.Enum):
    HIGHLY_EFFECTIVE = "highly_effective"
    EFFECTIVE = "effective"
    LIMITED_EFFECT = "limited_effect"
    INEFFECTIVE = "ineffective"
    NEGATIVE = "negative"


class MaintenanceIntervention(Base):
    __tablename__ = "maintenance_interventions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    machine_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("machines.id", ondelete="CASCADE"),
        nullable=False,
    )

    machine_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    intervention_type: Mapped[str] = mapped_column(String(150), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=MaintenanceInterventionStatus.PLANNED.value,
    )

    failure_prediction: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    recommendation: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    technician_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    before_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    after_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    verification_result: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    outcome_label: Mapped[str | None] = mapped_column(String(40), nullable=True)
    outcome_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    outcome_evidence: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("ix_maintenance_interventions_machine", "machine_id"),
        Index("ix_maintenance_interventions_type", "intervention_type"),
        Index("ix_maintenance_interventions_status", "status"),
        Index("ix_maintenance_interventions_machine_type", "machine_type"),
        Index("ix_maintenance_interventions_completed", "completed_at"),
    )
