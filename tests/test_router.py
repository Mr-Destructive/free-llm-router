import pytest

from free_llm_router.models import ChatRequest
from free_llm_router.providers import (
    Completion,
    KiloProvider,
    LLM7Provider,
    OVHProvider,
    Provider,
    ProviderError,
    ZenProvider,
    _clean_repeated,
    configured_providers,
    sorted_providers,
)
from free_llm_router.router import LLMRouter


class ProbeWorkingProvider(Provider):
    name = "probe-working"
    default_model = "probe-model"
    smartness = 60

    async def complete(self, request, model=None):
        return Completion("4", model or self.default_model, self.name)


class ProbeFailingProvider(Provider):
    name = "probe-failing"
    default_model = "probe-model"
    smartness = 60

    async def complete(self, request, model=None):
        raise ProviderError("down")


class FailingProvider(Provider):
    name = "fail"
    default_model = "fail-model"
    smartness = 100

    async def complete(self, request, model=None):
        raise ProviderError("unavailable")


class WorkingProvider(Provider):
    name = "working"
    default_model = "working-model"
    smartness = 10

    async def complete(self, request, model=None):
        return Completion("ok", model or self.default_model, self.name)


class SmarterProvider(Provider):
    name = "smarter"
    default_model = "smarter-model"
    smartness = 50

    async def complete(self, request, model=None):
        return Completion("smart", self.default_model, self.name)


@pytest.mark.asyncio
async def test_router_falls_back_to_next_provider():
    router = LLMRouter([FailingProvider(), WorkingProvider()])
    result = await router.complete(ChatRequest(messages=[{"role": "user", "content": "hi"}]))
    assert result.content == "ok"
    assert result.provider == "working"


@pytest.mark.asyncio
async def test_prefixed_model_selects_provider_and_model():
    router = LLMRouter([WorkingProvider()])
    result = await router.complete(ChatRequest(model="working:custom", messages=[{"role": "user", "content": "hi"}]))
    assert result.model == "custom"


@pytest.mark.asyncio
async def test_router_tries_smartest_provider_first():
    router = LLMRouter([WorkingProvider(), SmarterProvider()])
    result = await router.complete(ChatRequest(messages=[{"role": "user", "content": "hi"}]))
    assert result.provider == "smarter"


def test_providers_sorted_by_smartness_descending():
    ordered = sorted_providers([WorkingProvider(), SmarterProvider(), FailingProvider()])
    assert [p.name for p in ordered] == ["fail", "smarter", "working"]


def test_clean_repeated_dedupes_streamed_copies():
    assert _clean_repeated("ParisParisParis") == "Paris"
    assert _clean_repeated("hello worldhello world") in ("hello world", "hello worldhello world")


def test_configured_providers_include_anonymous_backbone():
    providers = configured_providers()
    names = {provider.name for provider in providers}
    assert names >= {"gemini", "zen", "kilo", "ovh", "llm7"}


def test_zen_model_order_prefers_primary_fallback():
    provider = ZenProvider()
    assert provider.fallback_models[0] == "big-pickle"


def test_kilo_uses_anonymous_gateway():
    provider = KiloProvider()
    assert provider.api_key is None
    assert provider.fallback_models[0] == "minimax/minimax-m3:free"


def test_ovh_uses_anonymous_endpoints():
    provider = OVHProvider()
    assert provider.api_key is None
    assert provider.fallback_models[0] == "gpt-oss-20b"


def test_llm7_uses_anonymous_turbo_tier():
    provider = LLM7Provider()
    assert provider.api_key is None
    assert provider.fallback_models[0] == "minimax-m2.7"


@pytest.mark.asyncio
async def test_probe_returns_alive_for_working_provider():
    alive, latency, model, error = await ProbeWorkingProvider().probe()
    assert alive is True
    assert latency >= 0
    assert model == "probe-model"
    assert error == ""


@pytest.mark.asyncio
async def test_probe_returns_dead_for_failing_provider():
    alive, latency, model, error = await ProbeFailingProvider().probe()
    assert alive is False
    assert model == ""
    assert "down" in error


def test_probe_result_dataclass():
    from free_llm_router.providers import ProbeResult
    result = ProbeResult("x", False, 1.5, "", "boom")
    assert result.name == "x"
    assert result.alive is False
    assert result.latency_ms == 1.5
    assert result.model == ""
    assert result.error == "boom"
