from typing import Any

import httpx

from src.common.config.config import LLMProviders
from src.common.exceptions import ProviderConfigurationException
from src.common.llm.interfaces import ChatMessage


class GoogleProvider:
    def __init__(
        self,
        *,
        api_key: str = LLMProviders.Google.API_KEY,
        api_base_url: str = LLMProviders.Google.API_BASE_URL,
        chat_model: str = LLMProviders.Google.CHAT_MODEL,
        embedding_model: str = LLMProviders.Google.EMBEDDING_MODEL,
        embedding_dimensions: int = LLMProviders.EMBEDDING_DIMENSIONS,
    ) -> None:
        if not api_key:
            raise ProviderConfigurationException("GOOGLE_API_KEY is required.")
        self._api_key = api_key
        self._api_base_url = api_base_url.rstrip("/")
        self._chat_model = chat_model
        self._embedding_model = embedding_model
        self._embedding_dimensions = embedding_dimensions

    async def chat_completion(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.2,
    ) -> str:
        url = (
            f"{self._api_base_url}/models/{self._chat_model}:generateContent"
            f"?key={self._api_key}"
        )
        payload = {
            "contents": [
                {
                    "role": "model" if message.role == "assistant" else "user",
                    "parts": [{"text": message.content}],
                }
                for message in messages
                if message.role != "system"
            ],
            "systemInstruction": {
                "parts": [
                    {
                        "text": "\n".join(
                            message.content
                            for message in messages
                            if message.role == "system"
                        )
                    }
                ]
            },
            "generationConfig": {"temperature": temperature},
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
        return self._extract_text(data)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        embeddings: list[list[float]] = []
        async with httpx.AsyncClient(timeout=60.0) as client:
            for text in texts:
                url = (
                    f"{self._api_base_url}/models/{self._embedding_model}:embedContent"
                    f"?key={self._api_key}"
                )
                payload = {
                    "model": f"models/{self._embedding_model}",
                    "content": {"parts": [{"text": text}]},
                    "outputDimensionality": self._embedding_dimensions,
                }
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                values = data["embedding"]["values"]
                embeddings.append([float(value) for value in values])
        return embeddings

    @staticmethod
    def _extract_text(data: dict[str, Any]) -> str:
        candidates = data.get("candidates", [])
        if not candidates:
            return ""
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        return "".join(str(part.get("text", "")) for part in parts)

