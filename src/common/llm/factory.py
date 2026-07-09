from src.common.config.config import LLMProviders
from src.common.exceptions import ProviderConfigurationException
from src.common.llm.google_provider import GoogleProvider
from src.common.llm.interfaces import LLMProvider
from src.common.llm.openai_provider import OpenAIProvider


class LLMProviderFactory:
    @staticmethod
    def create() -> LLMProvider:
        provider = LLMProviders.ACTIVE_PROVIDER.lower()
        if provider == "openai":
            return OpenAIProvider()
        if provider == "google":
            return GoogleProvider()
        raise ProviderConfigurationException(f"Unsupported LLM_PROVIDER: {provider}")

