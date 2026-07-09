from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from src.api.health import router as health_router
from src.common.config.config import AppConfig
from src.common.db.session import dispose_engine
from src.common.exceptions.handlers import register_exception_handlers
from src.common.logger.logger import get_logger
from src.journal.journal_router import router as journal_router

logger = get_logger("MiniMe-App")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Mini-Me application starting", extra={"app": AppConfig.NAME})
    yield
    await dispose_engine()
    logger.info("Mini-Me application stopped", extra={"app": AppConfig.NAME})


def create_app() -> FastAPI:
    app = FastAPI(
        title=AppConfig.NAME,
        version=AppConfig.VERSION,
        description="Personal AI memory API with journal storage and RAG retrieval.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(journal_router)
    return app


app = create_app()
