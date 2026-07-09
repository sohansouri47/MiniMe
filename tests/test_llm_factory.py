from typing import cast

from pytest import MonkeyPatch

from src.common.config.config import LLMProviders
from src.common.llm.factory import LLMProviderFactory
from src.common.llm.interfaces import ChatMessage, LLMProvider


class FakeProvider:
    async def chat_completion(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.2,
    ) -> str:
        return "ok"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2] for _ in texts]


def test_factory_selects_openai(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(LLMProviders, "ACTIVE_PROVIDER", "openai")
    monkeypatch.setattr("src.common.llm.factory.OpenAIProvider", FakeProvider)

    provider = LLMProviderFactory.create()

    assert isinstance(cast(object, provider), FakeProvider)


def test_factory_selects_google(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(LLMProviders, "ACTIVE_PROVIDER", "google")
    monkeypatch.setattr("src.common.llm.factory.GoogleProvider", FakeProvider)

    provider = LLMProviderFactory.create()

    assert isinstance(cast(object, provider), FakeProvider)


async def test_fake_provider_matches_protocol() -> None:
    provider: LLMProvider = FakeProvider()

    assert await provider.chat_completion([ChatMessage(role="user", content="hi")])
    assert await provider.embed(["hello"]) == [[0.1, 0.2]]
