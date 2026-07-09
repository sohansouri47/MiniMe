from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

LLMProviderName = Literal["openai", "google"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    APP_NAME: str = "Mini-Me"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://minime:minime@localhost:5432/minime",
    )
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    LLM_PROVIDER: LLMProviderName = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str | None = None
    OPENAI_CHAT_MODEL: str = "gpt-4.1-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    GOOGLE_API_KEY: str = ""
    GOOGLE_CHAT_MODEL: str = "gemini-1.5-flash"
    GOOGLE_EMBEDDING_MODEL: str = "text-embedding-004"
    GOOGLE_API_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"

    EMBEDDING_DIMENSIONS: int = 1536
    RAG_TOP_K: int = 5
    DEFAULT_USER_EMAIL: str = "default@mini-me.local"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


class AppConfig:
    NAME = settings.APP_NAME
    VERSION = settings.APP_VERSION
    ENV = settings.APP_ENV
    HOST = settings.HOST
    PORT = settings.PORT
    RELOAD = settings.RELOAD
    LOG_LEVEL = settings.LOG_LEVEL


class DatabaseConfig:
    URL = settings.DATABASE_URL
    POOL_SIZE = settings.DATABASE_POOL_SIZE
    MAX_OVERFLOW = settings.DATABASE_MAX_OVERFLOW


class LLMProviders:
    ACTIVE_PROVIDER = settings.LLM_PROVIDER
    EMBEDDING_DIMENSIONS = settings.EMBEDDING_DIMENSIONS

    class OpenAI:
        API_KEY = settings.OPENAI_API_KEY
        BASE_URL = settings.OPENAI_BASE_URL
        CHAT_MODEL = settings.OPENAI_CHAT_MODEL
        EMBEDDING_MODEL = settings.OPENAI_EMBEDDING_MODEL

    class Google:
        API_KEY = settings.GOOGLE_API_KEY
        API_BASE_URL = settings.GOOGLE_API_BASE_URL
        CHAT_MODEL = settings.GOOGLE_CHAT_MODEL
        EMBEDDING_MODEL = settings.GOOGLE_EMBEDDING_MODEL


class MemoryConfig:
    RAG_TOP_K = settings.RAG_TOP_K
    DEFAULT_USER_EMAIL = settings.DEFAULT_USER_EMAIL
