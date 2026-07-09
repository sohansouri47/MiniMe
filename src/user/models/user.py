from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.db.base import Base
from src.common.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from src.journal.models.chat_history import ChatHistory
    from src.journal.models.journal_entry import JournalEntry


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)

    journal_entries: Mapped[list[JournalEntry]] = relationship(
        "JournalEntry",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    chat_history: Mapped[list[ChatHistory]] = relationship(
        "ChatHistory",
        back_populates="user",
        cascade="all, delete-orphan",
    )
