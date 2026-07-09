from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class QueryRequest(BaseModel):
    user_email: EmailStr
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievedMemory(BaseModel):
    id: UUID
    title: str
    summary: str | None
    created_at: datetime


class QueryResponse(BaseModel):
    question: str
    answer: str
    memories: list[RetrievedMemory]

