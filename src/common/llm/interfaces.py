from typing import Protocol

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class LLMProvider(Protocol):
    async def chat_completion(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.2,
    ) -> str:
        ...

    async def embed(self, texts: list[str]) -> list[list[float]]:
        ...

