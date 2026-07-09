from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.db.base import Base
from src.common.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from src.user.models.user import User


class ChatHistory(Base, TimestampMixin):
    __tablename__ = "chat_history"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)

    user: Mapped[User] = relationship("User", back_populates="chat_history")
