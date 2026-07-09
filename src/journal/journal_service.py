from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.common.config.constants import Constants
from src.common.config.prompts import MemoryPrompts
from src.common.exceptions import NotFoundException
from src.common.llm.interfaces import ChatMessage, LLMProvider
from src.common.logger.logger import get_logger
from src.journal.journal_repo import JournalRepository
from src.journal.schemas.journal_schema import JournalCreate, JournalResponse
from src.journal.schemas.reindex_schema import ReindexRequest, ReindexResponse
from src.user.user_repo import UserRepository

logger = get_logger("MiniMe-JournalService")


class JournalService:
    def __init__(
        self,
        *,
        session: AsyncSession,
        user_repository: UserRepository,
        journal_repository: JournalRepository,
        llm_provider: LLMProvider,
    ) -> None:
        self._session = session
        self._user_repository = user_repository
        self._journal_repository = journal_repository
        self._llm_provider = llm_provider

    async def create_entry(self, payload: JournalCreate) -> JournalResponse:
        user = await self._user_repository.get_or_create_by_email(
            str(payload.user_email),
        )
        entry = await self._journal_repository.create(
            user_id=user.id,
            title=payload.title,
            transcript=payload.transcript,
        )
        logger.info("Journal entry saved", extra={"entry_id": entry.id})

        summary = await self._summarize(
            title=payload.title,
            transcript=payload.transcript,
        )
        embedding = await self._embed_entry(
            title=payload.title,
            transcript=payload.transcript,
            summary=summary,
        )
        await self._journal_repository.update_summary_embedding(
            entry,
            summary=summary,
            embedding=embedding,
        )
        await self._session.commit()
        await self._session.refresh(entry)
        logger.info("Journal entry indexed", extra={"entry_id": entry.id})
        return JournalResponse.model_validate(entry)

    async def list_entries(
        self,
        *,
        user_email: str,
        limit: int,
        offset: int,
    ) -> list[JournalResponse]:
        user = await self._user_repository.get_by_email(user_email)
        if user is None:
            return []
        entries = await self._journal_repository.list_by_user(
            user_id=user.id,
            limit=limit,
            offset=offset,
        )
        return [JournalResponse.model_validate(entry) for entry in entries]

    async def get_entry(
        self,
        *,
        entry_id: UUID,
        user_email: str,
    ) -> JournalResponse:
        user = await self._user_repository.get_by_email(user_email)
        if user is None:
            raise NotFoundException("Journal entry not found.")
        entry = await self._journal_repository.get_by_id_for_user(
            entry_id=entry_id,
            user_id=user.id,
        )
        if entry is None:
            raise NotFoundException("Journal entry not found.")
        return JournalResponse.model_validate(entry)

    async def delete_entry(
        self,
        *,
        entry_id: UUID,
        user_email: str,
    ) -> None:
        user = await self._user_repository.get_by_email(user_email)
        if user is None:
            raise NotFoundException("Journal entry not found.")
        deleted = await self._journal_repository.delete_by_id_for_user(
            entry_id=entry_id,
            user_id=user.id,
        )
        if not deleted:
            raise NotFoundException("Journal entry not found.")
        await self._session.commit()
        logger.info("Journal entry deleted", extra={"entry_id": entry_id})

    async def reindex_entries(self, payload: ReindexRequest) -> ReindexResponse:
        user_id = None
        if payload.user_email is not None:
            user = await self._user_repository.get_by_email(str(payload.user_email))
            if user is None:
                return ReindexResponse(reindexed_count=0)
            user_id = user.id

        entries = await self._journal_repository.list_entries_for_reindex(
            user_id=user_id,
        )
        for entry in entries:
            summary = await self._summarize(
                title=entry.title,
                transcript=entry.transcript,
            )
            embedding = await self._embed_entry(
                title=entry.title,
                transcript=entry.transcript,
                summary=summary,
            )
            await self._journal_repository.update_summary_embedding(
                entry,
                summary=summary,
                embedding=embedding,
            )
        await self._session.commit()
        logger.info("Journal reindex complete", extra={"count": len(entries)})
        return ReindexResponse(reindexed_count=len(entries))

    async def _summarize(self, *, title: str, transcript: str) -> str:
        return await self._llm_provider.chat_completion(
            [
                ChatMessage(
                    role=Constants.SYSTEM_ROLE,
                    content=MemoryPrompts.SUMMARY_SYSTEM,
                ),
                ChatMessage(
                    role=Constants.USER_ROLE,
                    content=MemoryPrompts.SUMMARY_USER_TEMPLATE.format(
                        title=title,
                        transcript=transcript,
                    ),
                ),
            ],
            temperature=0.1,
        )

    async def _embed_entry(
        self,
        *,
        title: str,
        transcript: str,
        summary: str,
    ) -> list[float]:
        text = f"Title: {title}\nSummary: {summary}\nTranscript: {transcript}"
        embeddings = await self._llm_provider.embed([text])
        return embeddings[0]
