from typing import Any, cast
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.journal.models.journal_entry import JournalEntry


class JournalRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: UUID,
        title: str,
        transcript: str,
    ) -> JournalEntry:
        entry = JournalEntry(
            user_id=user_id,
            title=title,
            transcript=transcript,
        )
        self._session.add(entry)
        await self._session.flush()
        return entry

    async def list_by_user(
        self,
        *,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[JournalEntry]:
        result = await self._session.execute(
            select(JournalEntry)
            .where(JournalEntry.user_id == user_id)
            .order_by(JournalEntry.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_id_for_user(
        self,
        *,
        entry_id: UUID,
        user_id: UUID,
    ) -> JournalEntry | None:
        result = await self._session.execute(
            select(JournalEntry).where(
                JournalEntry.id == entry_id,
                JournalEntry.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def delete_by_id_for_user(
        self,
        *,
        entry_id: UUID,
        user_id: UUID,
    ) -> bool:
        result = await self._session.execute(
            delete(JournalEntry).where(
                JournalEntry.id == entry_id,
                JournalEntry.user_id == user_id,
            )
        )
        return bool(cast(Any, result).rowcount)

    async def update_summary_embedding(
        self,
        entry: JournalEntry,
        *,
        summary: str,
        embedding: list[float],
    ) -> JournalEntry:
        entry.summary = summary
        entry.embedding = embedding
        await self._session.flush()
        return entry

    async def semantic_search(
        self,
        *,
        user_id: UUID,
        query_embedding: list[float],
        limit: int,
    ) -> list[JournalEntry]:
        distance = JournalEntry.embedding.cosine_distance(query_embedding)
        result = await self._session.execute(
            select(JournalEntry)
            .where(
                JournalEntry.user_id == user_id,
                JournalEntry.embedding.is_not(None),
            )
            .order_by(distance)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_entries_for_reindex(
        self,
        *,
        user_id: UUID | None = None,
    ) -> list[JournalEntry]:
        statement = select(JournalEntry).order_by(JournalEntry.created_at.asc())
        if user_id is not None:
            statement = statement.where(JournalEntry.user_id == user_id)
        result = await self._session.execute(statement)
        return list(result.scalars().all())
