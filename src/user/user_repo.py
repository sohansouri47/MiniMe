from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_or_create_by_email(self, email: str) -> User:
        user = await self.get_by_email(email)
        if user is not None:
            return user

        user = User(email=email)
        self._session.add(user)
        await self._session.flush()
        return user
