from uuid import UUID

from fastapi import APIRouter, status

from src.common.config.constants import Routes
from src.journal.journal_dependencies import JournalServiceDep, QueryServiceDep
from src.journal.schemas.journal_schema import JournalCreate, JournalResponse
from src.journal.schemas.query_schema import QueryRequest, QueryResponse
from src.journal.schemas.reindex_schema import ReindexRequest, ReindexResponse

router = APIRouter(prefix=Routes.API_V1_PREFIX)
journal_router = APIRouter(prefix="/journal", tags=["journal"])
query_router = APIRouter(tags=["query"])
reindex_router = APIRouter(tags=["reindex"])


@journal_router.post(
    "",
    response_model=JournalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_journal_entry(
    payload: JournalCreate,
    service: JournalServiceDep,
) -> JournalResponse:
    return await service.create_entry(payload)


@journal_router.get("", response_model=list[JournalResponse])
async def list_journal_entries(
    user_email: str,
    service: JournalServiceDep,
    limit: int = 50,
    offset: int = 0,
) -> list[JournalResponse]:
    return await service.list_entries(user_email=user_email, limit=limit, offset=offset)


@journal_router.get("/{entry_id}", response_model=JournalResponse)
async def get_journal_entry(
    entry_id: UUID,
    user_email: str,
    service: JournalServiceDep,
) -> JournalResponse:
    return await service.get_entry(entry_id=entry_id, user_email=user_email)


@journal_router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_journal_entry(
    entry_id: UUID,
    user_email: str,
    service: JournalServiceDep,
) -> None:
    await service.delete_entry(entry_id=entry_id, user_email=user_email)


@query_router.post("/query", response_model=QueryResponse)
async def query_memories(
    payload: QueryRequest,
    service: QueryServiceDep,
) -> QueryResponse:
    return await service.answer_question(payload)


@reindex_router.post("/reindex", response_model=ReindexResponse)
async def reindex_entries(
    payload: ReindexRequest,
    service: JournalServiceDep,
) -> ReindexResponse:
    return await service.reindex_entries(payload)


router.include_router(journal_router)
router.include_router(query_router)
router.include_router(reindex_router)

