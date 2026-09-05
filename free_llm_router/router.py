from __future__ import annotations

from .models import ChatRequest
from .providers import Completion, Provider, ProviderError, sorted_providers


class NoProviderAvailable(RuntimeError):
    pass


class LLMRouter:
    def __init__(self, providers: list[Provider]) -> None:
        # Smartest providers first; weaker ones are fallbacks.
        self.providers = sorted_providers(providers)

    async def complete(self, request: ChatRequest) -> Completion:
        wanted_provider, separator, wanted_model = request.model.partition(":")
        candidates = self.providers
        if separator:
            candidates = [provider for provider in self.providers if provider.name == wanted_provider]
        errors = []
        for provider in candidates:
            try:
                return await provider.complete(request, wanted_model if separator else None)
            except ProviderError as error:
                errors.append(str(error))
        detail = "; ".join(errors) or "no configured provider matches the requested model"
        raise NoProviderAvailable(detail)

