from sqlalchemy.ext.asyncio import AsyncSession

from src.common.config.constants import Constants
from src.common.config.prompts import MemoryPrompts
from src.common.exceptions import NotFoundException
from src.common.llm.interfaces import ChatMessage, LLMProvider
from src.common.logger.logger import get_logger
from src.journal.chat_history_repo import ChatHistoryRepository
from src.journal.journal_repo import JournalRepository
from src.journal.models.journal_entry import JournalEntry
from src.journal.schemas.query_schema import (
    QueryRequest,
    QueryResponse,
    RetrievedMemory,
)
from src.user.user_repo import UserRepository

import httpx

logger = get_logger("MiniMe-QueryService")


class QueryService:
    def __init__(
        self,
        *,
        session: AsyncSession,
        user_repository: UserRepository,
        journal_repository: JournalRepository,
        chat_history_repository: ChatHistoryRepository,
        llm_provider: LLMProvider,
    ) -> None:
        self._session = session
        self._user_repository = user_repository
        self._journal_repository = journal_repository
        self._chat_history_repository = chat_history_repository
        self._llm_provider = llm_provider

    async def answer_question(self, payload: QueryRequest) -> QueryResponse:
        user = await self._user_repository.get_by_email(str(payload.user_email))
        if user is None:
            raise NotFoundException("No memories found for this user.")

        query_embedding = (await self._llm_provider.embed([payload.question]))[0]
        entries = await self._journal_repository.semantic_search(
            user_id=user.id,
            query_embedding=query_embedding,
            limit=payload.top_k,
        )
        context = self._build_context(entries)
        answer = await self._llm_provider.chat_completion(
            [
                ChatMessage(
                    role=Constants.SYSTEM_ROLE,
                    content=MemoryPrompts.RAG_SYSTEM,
                ),
                ChatMessage(
                    role=Constants.USER_ROLE,
                    content=MemoryPrompts.RAG_USER_TEMPLATE.format(
                        question=payload.question,
                        context=context,
                    ),
                ),
            ],
            temperature=0.2,
        )

        await self._chat_history_repository.create(
            user_id=user.id,
            question=payload.question,
            answer=answer,
        )
        await self._session.commit()
        logger.info(
            "Query answered",
            extra={"user_id": user.id, "memory_count": len(entries)},
        )
        return QueryResponse(
            question=payload.question,
            answer=answer,
            memories=[
                RetrievedMemory(
                    id=entry.id,
                    title=entry.title,
                    summary=entry.summary,
                    created_at=entry.created_at,
                )
                for entry in entries
            ],
        )

    @staticmethod
    def _build_context(entries: list[JournalEntry]) -> str:
        if not entries:
            return "No relevant memories were retrieved."
        return "\n\n".join(
            (
                f"Memory {index}\n"
                f"Title: {entry.title}\n"
                f"Created at: {entry.created_at.isoformat()}\n"
                f"Summary: {entry.summary or 'No summary'}\n"
                f"Transcript: {entry.transcript}"
            )
            for index, entry in enumerate(entries, start=1)
        )
