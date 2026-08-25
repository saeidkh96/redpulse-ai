import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.machine import MachineStatus


class MachineBase(BaseModel):
    machine_code: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)
    manufacturer: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, max_length=255)
    machine_type: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=255)
    installation_date: date | None = None
    metadata: dict = Field(default_factory=dict)


class MachineCreate(MachineBase):
    status: MachineStatus = MachineStatus.ACTIVE


class MachineUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    manufacturer: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, max_length=255)
    machine_type: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=255)
    installation_date: date | None = None
    status: MachineStatus | None = None
    metadata: dict | None = None


class MachineRead(MachineBase):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: uuid.UUID
    status: MachineStatus
    metadata: dict = Field(validation_alias="metadata_")
    created_at: datetime
    updated_at: datetime
