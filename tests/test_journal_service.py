from datetime import UTC, datetime
from typing import cast
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.llm.interfaces import ChatMessage
from src.journal.journal_repo import JournalRepository
from src.journal.journal_service import JournalService
from src.journal.schemas.journal_schema import JournalCreate
from src.journal.schemas.reindex_schema import ReindexRequest
from src.user.user_repo import UserRepository


class FakeSession:
    def __init__(self) -> None:
        self.committed = False

    async def commit(self) -> None:
        self.committed = True


class FakeUser:
    def __init__(self, email: str) -> None:
        self.id = uuid4()
        self.email = email


class FakeEntry:
    def __init__(self, *, user_id: UUID, title: str, transcript: str) -> None:
        self.id = uuid4()
        self.user_id = user_id
        self.title = title
        self.transcript = transcript
        self.summary: str | None = None
        self.embedding: list[float] | None = None
        self.created_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)


class FakeUserRepository:
    def __init__(self) -> None:
        self.user: FakeUser | None = None

    async def get_or_create_by_email(self, email: str) -> FakeUser:
        self.user = self.user or FakeUser(email)
        return self.user

    async def get_by_email(self, email: str) -> FakeUser | None:
        return self.user if self.user and self.user.email == email else None


class FakeJournalRepository:
    def __init__(self) -> None:
        self.entries: list[FakeEntry] = []

    async def create(
        self,
        *,
        user_id: UUID,
        title: str,
        transcript: str,
    ) -> FakeEntry:
        entry = FakeEntry(user_id=user_id, title=title, transcript=transcript)
        self.entries.append(entry)
        return entry

    async def update_summary_embedding(
        self,
        entry: FakeEntry,
        *,
        summary: str,
        embedding: list[float],
    ) -> FakeEntry:
        entry.summary = summary
        entry.embedding = embedding
        return entry

    async def list_entries_for_reindex(
        self,
        *,
        user_id: UUID | None = None,
    ) -> list[FakeEntry]:
        return self.entries


class FakeLLMProvider:
    async def chat_completion(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.2,
    ) -> str:
        return "summary"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


@pytest.mark.asyncio
async def test_create_entry_summarizes_embeds_and_commits() -> None:
    session = FakeSession()
    user_repository = FakeUserRepository()
    journal_repository = FakeJournalRepository()
    service = JournalService(
        session=cast(AsyncSession, session),
        user_repository=cast(UserRepository, user_repository),
        journal_repository=cast(JournalRepository, journal_repository),
        llm_provider=FakeLLMProvider(),
    )

    response = await service.create_entry(
        JournalCreate(
            user_email="you@example.com",
            title="A day",
            transcript="I remembered something important.",
        )
    )

    assert response.summary == "summary"
    assert journal_repository.entries[0].embedding == [0.1, 0.2, 0.3]
    assert session.committed


@pytest.mark.asyncio
async def test_reindex_updates_existing_entries() -> None:
    session = FakeSession()
    user_repository = FakeUserRepository()
    user = await user_repository.get_or_create_by_email("you@example.com")
    journal_repository = FakeJournalRepository()
    await journal_repository.create(
        user_id=user.id,
        title="Existing",
        transcript="Old memory",
    )
    service = JournalService(
        session=cast(AsyncSession, session),
        user_repository=cast(UserRepository, user_repository),
        journal_repository=cast(JournalRepository, journal_repository),
        llm_provider=FakeLLMProvider(),
    )

    response = await service.reindex_entries(
        ReindexRequest(user_email="you@example.com")
    )

    assert response.reindexed_count == 1
    assert journal_repository.entries[0].summary == "summary"
    assert session.committed
