from typing import Any, cast

from openai import AsyncOpenAI

from src.common.config.config import LLMProviders
from src.common.exceptions import ProviderConfigurationException
from src.common.llm.interfaces import ChatMessage


class OpenAIProvider:
    def __init__(
        self,
        *,
        api_key: str = LLMProviders.OpenAI.API_KEY,
        base_url: str | None = LLMProviders.OpenAI.BASE_URL,
        chat_model: str = LLMProviders.OpenAI.CHAT_MODEL,
        embedding_model: str = LLMProviders.OpenAI.EMBEDDING_MODEL,
        embedding_dimensions: int = LLMProviders.EMBEDDING_DIMENSIONS,
    ) -> None:
        if not api_key:
            self._client = None
        else:
            self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._chat_model = chat_model
        self._embedding_model = embedding_model
        self._embedding_dimensions = embedding_dimensions

    async def chat_completion(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.2,
    ) -> str:
        if self._client is None:
            return "This is a mock chat completion response because no OPENAI_API_KEY was provided."
        response = await self._client.chat.completions.create(
            model=self._chat_model,
            messages=cast(Any, [message.model_dump() for message in messages]),
            temperature=temperature,
        )
        content = response.choices[0].message.content
        return content or ""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if self._client is None:
            return [[0.0] * self._embedding_dimensions for _ in texts]
        response = await self._client.embeddings.create(
            model=self._embedding_model,
            input=texts,
            dimensions=self._embedding_dimensions,
        )
        return [item.embedding for item in response.data]
