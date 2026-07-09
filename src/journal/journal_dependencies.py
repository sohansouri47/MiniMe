from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.db.session import get_session
from src.common.llm.factory import LLMProviderFactory
from src.common.llm.interfaces import LLMProvider
from src.journal.chat_history_repo import ChatHistoryRepository
from src.journal.journal_repo import JournalRepository
from src.journal.journal_service import JournalService
from src.journal.query_service import QueryService
from src.user.user_repo import UserRepository


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async for session in get_session():
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_llm_provider() -> LLMProvider:
    return LLMProviderFactory.create()


LlmProviderDep = Annotated[LLMProvider, Depends(get_llm_provider)]


def get_journal_service(
    session: DbSession,
    llm_provider: LlmProviderDep,
) -> JournalService:
    return JournalService(
        session=session,
        user_repository=UserRepository(session),
        journal_repository=JournalRepository(session),
        llm_provider=llm_provider,
    )


def get_query_service(
    session: DbSession,
    llm_provider: LlmProviderDep,
) -> QueryService:
    return QueryService(
        session=session,
        user_repository=UserRepository(session),
        journal_repository=JournalRepository(session),
        chat_history_repository=ChatHistoryRepository(session),
        llm_provider=llm_provider,
    )


JournalServiceDep = Annotated[JournalService, Depends(get_journal_service)]
QueryServiceDep = Annotated[QueryService, Depends(get_query_service)]

