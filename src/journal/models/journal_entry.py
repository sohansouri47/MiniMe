from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.config.config import LLMProviders
from src.common.db.base import Base
from src.common.db.mixins import UpdatedTimestampMixin

if TYPE_CHECKING:
    from src.user.models.user import User


class JournalEntry(Base, UpdatedTimestampMixin):
    __tablename__ = "journal_entries"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    transcript: Mapped[str] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(LLMProviders.EMBEDDING_DIMENSIONS),
        nullable=True,
    )

    user: Mapped[User] = relationship("User", back_populates="journal_entries")
