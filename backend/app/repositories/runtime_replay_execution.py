from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import or_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.runtime_replay_execution import RuntimeReplayExecution


class RuntimeReplayExecutionRepository:
    async def get(
        self,
        session: AsyncSession,
        execution_key: str,
    ) -> RuntimeReplayExecution | None:
        result = await session.execute(
            select(RuntimeReplayExecution).where(
                RuntimeReplayExecution.execution_key == execution_key
            )
        )
        return result.scalar_one_or_none()

    async def try_claim(
        self,
        session: AsyncSession,
        *,
        execution_key: str,
        tenant_id: str,
        workflow_id: str,
        stage_name: str,
        lease_owner: str,
        lease_seconds: float,
    ) -> bool:
        if lease_seconds <= 0:
            raise ValueError("lease_seconds must be greater than 0")

        now = datetime.now(timezone.utc)
        lease_expires_at = now + timedelta(seconds=lease_seconds)

        statement = (
            insert(RuntimeReplayExecution)
            .values(
                execution_key=execution_key,
                tenant_id=tenant_id,
                workflow_id=workflow_id,
                stage_name=stage_name,
                state="running",
                attempts=0,
                value=None,
                error=None,
                lease_owner=lease_owner,
                lease_expires_at=lease_expires_at,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    RuntimeReplayExecution.execution_key,
                ]
            )
            .returning(RuntimeReplayExecution.execution_key)
        )

        result = await session.execute(statement)
        claimed_key = result.scalar_one_or_none()

        await session.commit()

        return claimed_key is not None

    async def try_takeover_stale_claim(
        self,
        session: AsyncSession,
        *,
        execution_key: str,
        tenant_id: str,
        lease_owner: str,
        lease_seconds: float,
    ) -> bool:
        if lease_seconds <= 0:
            raise ValueError("lease_seconds must be greater than 0")

        now = datetime.now(timezone.utc)
        lease_expires_at = now + timedelta(seconds=lease_seconds)

        statement = (
            update(RuntimeReplayExecution)
            .where(
                RuntimeReplayExecution.execution_key == execution_key,
                RuntimeReplayExecution.tenant_id == tenant_id,
                RuntimeReplayExecution.state == "running",
                or_(
                    RuntimeReplayExecution.lease_expires_at.is_(None),
                    RuntimeReplayExecution.lease_expires_at <= now,
                ),
            )
            .values(
                lease_owner=lease_owner,
                lease_expires_at=lease_expires_at,
                error=None,
            )
            .returning(RuntimeReplayExecution.execution_key)
        )

        result = await session.execute(statement)
        claimed_key = result.scalar_one_or_none()

        await session.commit()

        return claimed_key is not None

    async def renew_lease(
        self,
        session: AsyncSession,
        *,
        execution_key: str,
        tenant_id: str,
        lease_owner: str,
        lease_seconds: float,
    ) -> bool:
        if lease_seconds <= 0:
            raise ValueError("lease_seconds must be greater than 0")

        lease_expires_at = datetime.now(
            timezone.utc
        ) + timedelta(seconds=lease_seconds)

        statement = (
            update(RuntimeReplayExecution)
            .where(
                RuntimeReplayExecution.execution_key == execution_key,
                RuntimeReplayExecution.tenant_id == tenant_id,
                RuntimeReplayExecution.state == "running",
                RuntimeReplayExecution.lease_owner == lease_owner,
            )
            .values(
                lease_expires_at=lease_expires_at,
                updated_at=datetime.now(timezone.utc),
            )
            .returning(RuntimeReplayExecution.execution_key)
        )

        result = await session.execute(statement)
        renewed_key = result.scalar_one_or_none()

        await session.commit()

        return renewed_key is not None

    async def save_owned(
        self,
        session: AsyncSession,
        *,
        execution_key: str,
        tenant_id: str,
        workflow_id: str,
        stage_name: str,
        lease_owner: str,
        state: str,
        attempts: int,
        value: dict | None = None,
        error: str | None = None,
        lease_seconds: float | None = None,
        terminal: bool = False,
    ) -> RuntimeReplayExecution:
        values: dict = {
            "workflow_id": workflow_id,
            "stage_name": stage_name,
            "state": state,
            "attempts": attempts,
            "value": value,
            "error": error,
            "updated_at": datetime.now(timezone.utc),
        }

        if terminal:
            values["lease_owner"] = None
            values["lease_expires_at"] = None
        else:
            if lease_seconds is None or lease_seconds <= 0:
                raise ValueError(
                    "lease_seconds must be greater than 0 "
                    "for non-terminal writes"
                )

            values["lease_expires_at"] = datetime.now(
                timezone.utc
            ) + timedelta(seconds=lease_seconds)

        statement = (
            update(RuntimeReplayExecution)
            .where(
                RuntimeReplayExecution.execution_key == execution_key,
                RuntimeReplayExecution.tenant_id == tenant_id,
                RuntimeReplayExecution.lease_owner == lease_owner,
                RuntimeReplayExecution.state == "running",
            )
            .values(**values)
            .returning(RuntimeReplayExecution.execution_key)
        )

        result = await session.execute(statement)
        updated_key = result.scalar_one_or_none()

        if updated_key is None:
            await session.rollback()
            raise RuntimeError(
                "runtime replay lease ownership was lost"
            )

        await session.commit()

        record = await self.get(session, execution_key)

        if record is None:
            raise RuntimeError(
                "runtime replay execution disappeared after update"
            )

        return record

    async def clear_failed(
        self,
        session: AsyncSession,
        execution_key: str,
    ) -> bool:
        record = await self.get(session, execution_key)

        if record is None or record.state != "failed":
            return False

        await session.delete(record)
        await session.commit()

        return True


runtime_replay_execution_repository = RuntimeReplayExecutionRepository()
