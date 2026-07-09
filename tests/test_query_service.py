from datetime import UTC, datetime
from typing import cast
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.llm.interfaces import ChatMessage
from src.journal.chat_history_repo import ChatHistoryRepository
from src.journal.journal_repo import JournalRepository
from src.journal.query_service import QueryService
from src.journal.schemas.query_schema import QueryRequest
from src.user.user_repo import UserRepository


class FakeSession:
    def __init__(self) -> None:
        self.committed = False

    async def commit(self) -> None:
        self.committed = True


class FakeUser:
    def __init__(self) -> None:
        self.id = uuid4()
        self.email = "you@example.com"


class FakeEntry:
    def __init__(self, *, user_id: UUID) -> None:
        self.id = uuid4()
        self.user_id = user_id
        self.title = "Memory"
        self.transcript = "We went hiking."
        self.summary = "A hiking memory."
        self.created_at = datetime.now(UTC)


class FakeUserRepository:
    def __init__(self, user: FakeUser) -> None:
        self.user = user

    async def get_by_email(self, email: str) -> FakeUser | None:
        return self.user if email == self.user.email else None


class FakeJournalRepository:
    def __init__(self, entry: FakeEntry) -> None:
        self.entry = entry

    async def semantic_search(
        self,
        *,
        user_id: UUID,
        query_embedding: list[float],
        limit: int,
    ) -> list[FakeEntry]:
        return [self.entry]


class FakeChatHistoryRepository:
    def __init__(self) -> None:
        self.rows: list[tuple[UUID, str, str]] = []

    async def create(
        self,
        *,
        user_id: UUID,
        question: str,
        answer: str,
    ) -> object:
        self.rows.append((user_id, question, answer))
        return object()


class FakeLLMProvider:
    async def chat_completion(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.2,
    ) -> str:
        return "You went hiking."

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


@pytest.mark.asyncio
async def test_answer_question_retrieves_answers_and_stores_history() -> None:
    session = FakeSession()
    user = FakeUser()
    chat_history_repository = FakeChatHistoryRepository()
    service = QueryService(
        session=cast(AsyncSession, session),
        user_repository=cast(UserRepository, FakeUserRepository(user)),
        journal_repository=cast(
            JournalRepository,
            FakeJournalRepository(FakeEntry(user_id=user.id)),
        ),
        chat_history_repository=cast(
            ChatHistoryRepository,
            chat_history_repository,
        ),
        llm_provider=FakeLLMProvider(),
    )

    response = await service.answer_question(
        QueryRequest(
            user_email="you@example.com",
            question="What did I do?",
            top_k=3,
        )
    )

    assert response.answer == "You went hiking."
    assert response.memories[0].title == "Memory"
    assert chat_history_repository.rows[0][1] == "What did I do?"
    assert session.committed
