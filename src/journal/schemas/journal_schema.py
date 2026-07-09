from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class JournalCreate(BaseModel):
    user_email: EmailStr
    title: str = Field(min_length=1, max_length=255)
    transcript: str = Field(min_length=1)


class JournalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    transcript: str
    summary: str | None
    created_at: datetime
    updated_at: datetime

