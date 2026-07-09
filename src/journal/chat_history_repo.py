from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.journal.models.chat_history import ChatHistory


class ChatHistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: UUID,
        question: str,
        answer: str,
    ) -> ChatHistory:
        chat_history = ChatHistory(
            user_id=user_id,
            question=question,
            answer=answer,
        )
        self._session.add(chat_history)
        await self._session.flush()
        return chat_history
