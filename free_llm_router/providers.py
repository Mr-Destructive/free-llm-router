from __future__ import annotations

import asyncio
import json
import os
import re
import time
import uuid
from dataclasses import dataclass
from typing import Any

import httpx

from .models import ChatRequest


class ProviderError(RuntimeError):
    """A provider did not produce a usable completion."""


def _plain_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(str(part.get("text", "")) for part in content if isinstance(part, dict))
    return ""


def _messages(request: ChatRequest) -> list[dict[str, str]]:
    return [
        {"role": message.role, "content": _plain_content(message.content)}
        for message in request.messages
    ]


def _last_user_message(request: ChatRequest) -> str:
    for message in reversed(request.messages):
        if message.role == "user":
            return _plain_content(message.content)
    return _plain_content(request.messages[0].content)


@dataclass(frozen=True)
class Completion:
    content: str
    model: str
    provider: str


class Provider:
    """A cloud completion provider.

    ``smartness`` ranks providers; higher values run first ("smarter"),
    lower values are used only as fallback when the smarter providers fail.
    """
    name: str
    default_model: str
    smartness: int = 0

    async def complete(self, request: ChatRequest, model: str | None = None) -> Completion:
        raise NotImplementedError

    async def probe(self) -> tuple[bool, float, str, str]:
        """Lightweight health check: send ``2+2?`` and return (alive, latency_ms, model, error)."""
        start = time.monotonic()
        try:
            request = ChatRequest(
                messages=[{"role": "user", "content": "What is 2+2? Reply with just the number."}],
                max_tokens=20,
            )
            completion = await self.complete(request)
            latency = (time.monotonic() - start) * 1000
            return True, latency, completion.model, ""
        except Exception as error:
            latency = (time.monotonic() - start) * 1000
            return False, latency, "", str(error)


class OpenAICompatibleProvider(Provider):
    endpoint: str
    api_key: str | None = None
    env_key: str | None = None
    user_agent: str | None = None

    def __init__(self) -> None:
        if self.env_key:
            self.api_key = os.getenv(self.env_key)

    async def complete(self, request: ChatRequest, model: str | None = None) -> Completion:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if self.user_agent:
            headers["User-Agent"] = self.user_agent
        body: dict[str, Any] = {
            "model": model or self.default_model,
            "messages": _messages(request),
            "stream": False,
        }
        if request.temperature is not None:
            body["temperature"] = request.temperature
        if request.max_tokens is not None:
            body["max_tokens"] = request.max_tokens
        try:
            async with httpx.AsyncClient(timeout=90) as client:
                response = await client.post(self.endpoint, headers=headers, json=body)
            response.raise_for_status()
            payload = response.json()
            content = self._response_content(payload)
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as error:
            raise ProviderError(f"{self.name} failed: {error}") from error
        if not content:
            raise ProviderError(f"{self.name} returned an empty completion")
        return Completion(str(content), str(payload.get("model", body["model"])), self.name)

    def _response_content(self, payload: dict[str, Any]) -> str:
        """Extract the assistant's answer, falling back to its reasoning.

        Some backends (Kilo's nemotron/oss routes, OVH's gpt-oss) stream the
        thinking chain in ``message.reasoning`` while ``content`` stays null;
        accept that rather than declaring an empty completion.
        """
        message = payload["choices"][0]["message"]
        content = message.get("content")
        if content:
            return _plain_content(content)
        return _plain_content(message.get("reasoning", ""))


class GroqProvider(OpenAICompatibleProvider):
    name = "groq"
    endpoint = "https://api.groq.com/openai/v1/chat/completions"
    default_model = "llama-3.3-70b-versatile"
    env_key = "GROQ_API_KEY"
    smartness = 40


class OpenRouterProvider(OpenAICompatibleProvider):
    name = "openrouter"
    endpoint = "https://openrouter.ai/api/v1/chat/completions"
    default_model = "deepseek/deepseek-chat:free"
    env_key = "OPENROUTER_API_KEY"
    smartness = 60


class MistralProvider(OpenAICompatibleProvider):
    name = "mistral"
    endpoint = "https://api.mistral.ai/v1/chat/completions"
    default_model = "open-mistral-nemo"
    env_key = "MISTRAL_API_KEY"
    smartness = 20


class CloudflareProvider(OpenAICompatibleProvider):
    name = "cloudflare"
    endpoint = (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{os.getenv('CLOUDFLARE_ACCOUNT_ID', '')}/ai/v1/chat/completions"
    )
    default_model = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"
    env_key = "CLOUDFLARE_API_TOKEN"
    smartness = 30


class ZenProvider(OpenAICompatibleProvider):
    """opencode's anonymous free tier.

    ``https://opencode.ai/zen/v1`` serves free models to anyone presenting
    ``Authorization: Bearer public`` and opencode's User-Agent. Each model is a
    distinct free quota bucket, so the provider tries them in order and moves on
    when one is saturated or down.
    """
    name = "zen"
    endpoint = "https://opencode.ai/zen/v1/chat/completions"
    default_model = "big-pickle"
    # Tried in order until one returns (the free tier is per-model rate-limited).
    fallback_models = [
        "big-pickle",
        "mimo-v2.5-free",
        "nemotron-3.5-lightning-free",
    ]
    api_key = "public"  # anonymous bearer token
    user_agent = "opencode/1.2.31"
    smartness = 70
    env_key = None

    async def complete(self, request: ChatRequest, model: str | None = None) -> Completion:
        models = [model] if model else [*self.fallback_models]
        last_error: Exception | None = None
        for candidate in models:
            try:
                completion = await super().complete(request, candidate)
                if completion.content:
                    return completion
            except ProviderError as error:
                last_error = error
            await asyncio.sleep(0.2)
        raise ProviderError(f"zen failed: {last_error}") from last_error


class KiloProvider(OpenAICompatibleProvider):
    """Kilo.ai's gateway, which serves OpenRouter-style ``:free`` models anonymously.

    No API key is required for ``:free`` routes at ``api.kilo.ai/api/gateway``.
    Each model is a separate free quota bucket, so alternate through
    ``fallback_models`` when one is saturated or transiently unavailable.
    """
    name = "kilo"
    endpoint = "https://api.kilo.ai/api/gateway/v1/chat/completions"
    default_model = "minimax/minimax-m3:free"
    fallback_models = [
        "minimax/minimax-m3:free",
        "poolside/laguna-s-2.1:free",
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "kilo-auto/small",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "liquid/lfm-2.5-2.6b:free",
    ]
    smartness = 75
    env_key = None

    async def complete(self, request: ChatRequest, model: str | None = None) -> Completion:
        models = [model] if model else [*self.fallback_models]
        last_error: Exception | None = None
        for candidate in models:
            try:
                completion = await super().complete(request, candidate)
                if completion.content:
                    return completion
            except ProviderError as error:
                last_error = error
            await asyncio.sleep(0.2)
        raise ProviderError(f"kilo failed: {last_error}") from last_error


class OVHProvider(OpenAICompatibleProvider):
    """OVHcloud AI Endpoints' anonymous free tier.

    ``https://oai.endpoints.kepler.ai.cloud.ovh.net`` serves the open-weight
    models listed under ``/v1/models`` to unauthenticated callers at ~2 RPM
    per model from a shared pool (often 429 under load), so it sits low in the
    fallback order and tries a couple of models before giving up.
    """
    name = "ovh"
    endpoint = "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/chat/completions"
    default_model = "gpt-oss-20b"
    fallback_models = ["gpt-oss-20b", "gpt-oss-120b", "Qwen3-32B", "Qwen3.5-9B"]
    smartness = 55
    env_key = None

    async def complete(self, request: ChatRequest, model: str | None = None) -> Completion:
        models = [model] if model else [*self.fallback_models]
        last_error: Exception | None = None
        for candidate in models:
            try:
                completion = await super().complete(request, candidate)
                if completion.content:
                    return completion
            except ProviderError as error:
                last_error = error
            await asyncio.sleep(0.3)
        raise ProviderError(f"ovh failed: {last_error}") from last_error


class LLM7Provider(OpenAICompatibleProvider):
    """LLM7.io's anonymous ``turbo`` tier.

    ``https://api.llm7.io/v1`` serves a small set of chat models with no API
    key or signup. The free tier is per-model rate-limited (429s), so this
    provider cycles through its models before giving up. Models with strong
    reasoning output the answer in ``content`` after a ``reasoning_content``
    preface, which the base class already handles.
    """
    name = "llm7"
    endpoint = "https://api.llm7.io/v1/chat/completions"
    default_model = "minimax-m2.7"
    fallback_models = [
        "minimax-m2.7",
        "gpt-oss",
        "mistral-Nemo-Instruct-2407",
        "codestral-latest",
    ]
    smartness = 50
    env_key = None

    async def complete(self, request: ChatRequest, model: str | None = None) -> Completion:
        models = [model] if model else [*self.fallback_models]
        last_error: Exception | None = None
        for candidate in models:
            try:
                completion = await super().complete(request, candidate)
                if completion.content:
                    return completion
            except ProviderError as error:
                last_error = error
            await asyncio.sleep(0.2)
        raise ProviderError(f"llm7 failed: {last_error}") from last_error


def _clean_repeated(raw: str) -> str:
    """Gemini streams the same answer several times; keep one copy.

    Finds the longest substring that repeats immediately after itself and
    returns a single copy. Falls back to trimming whitespace.
    """
    text = raw.strip()
    n = len(text)
    best: str | None = None
    best_len = 0
    for i in range(n):
        max_len = min((n - i) // 2, 6000)
        for length in range(max_len, 0, -1):
            if text[i:i + length] == text[i + length:i + 2 * length]:
                if length > best_len:
                    best_len = length
                    best = text[i:i + length]
                break
    result = best if best is not None else text
    return _strip_gemini_artifacts(result)


def _strip_gemini_artifacts(text: str) -> str:
    """Remove Gemini's code-runner annotation fenced blocks.

    Gemini wraps executed-code output in fences with ``?code_`` URL markers
    (e.g. `` ```python?code_reference``` ``). Prefer the plain prose answer,
    dropping those annotation blocks but keeping a plain ``text``/``stdout``
    result when it is the whole answer.
    """
    if not text:
        return text
    annotation = re.compile(
        r"```[^`\n]*\?[^`\n]*code_[a-z_]+[^\n]*\n[\s\S]*?```", re.DOTALL
    )
    stripped = annotation.sub("", text)
    stripped = re.sub(r"\n{3,}", "\n\n", stripped)
    stripped = stripped.strip()
    if stripped:
        return stripped
    fence = re.compile(r"```(?:text|stdout)?[^`\n]*\n[\s\S]*?```", re.DOTALL)
    return fence.sub("", text).strip()


class GeminiProvider(Provider):
    """Google Gemini's anonymous web endpoint.

    Gemini's web app exposes an undocumented streaming RPC that works for
    anonymous, not-logged-in users. Replicating the browser handshake — the
    ``_reqid``/``f.sid`` query parameters and the ``x-goog-ext-*`` JSPB headers
    carrying fresh random UUIDs — is enough to get answers with no API key or
    login. The gemini-proxy approach, completed with those headers/params.
    """
    name = "gemini"
    default_model = "gemini-2.5-flash"
    smartness = 100

    _BASE = "https://gemini.google.com"
    _ENDPOINT = "/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate"
    _USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) HeadlessChrome/151.0.7922.34 Safari/537.36"
    )

    def __init__(self) -> None:
        self._conversation: list[str | None] = [None, None]

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": self._BASE,
            "Referer": f"{self._BASE}/",
            "User-Agent": self._USER_AGENT,
            "x-same-domain": "1",
            "x-goog-ext-525001261-jspb": json.dumps(
                [1, None, None, None, "cf41b0e0dd7d53e5", None, None, 0,
                 [4, 6, 4, 6], None, None, 1, None, None, 6, None, str(uuid.uuid4())]
            ).replace(" ", ""),
            "x-goog-ext-525005358-jspb": json.dumps([str(uuid.uuid4()), 1]).replace(" ", ""),
            "x-goog-ext-73010989-jspb": "[0]",
            "x-goog-ext-73010990-jspb": "[0,0,0]",
            "Accept-Language": "en-US",
        }

    def _extract(self, body: str) -> Completion:
        if body.startswith(")]}'"):
            body = body[4:]
        parts: list[str] = []
        for line in body.split("\n"):
            line = line.strip()
            if not line.startswith("[["):
                continue
            try:
                data = json.loads(line)
            except (json.JSONDecodeError, TypeError):
                continue
            for item in data:
                if not (isinstance(item, list) and len(item) >= 3 and item[0] == "wrb.fr" and item[2]):
                    continue
                try:
                    inner = json.loads(item[2])
                except (json.JSONDecodeError, TypeError):
                    continue
                if (isinstance(inner, list) and len(inner) > 1
                        and isinstance(inner[1], list) and len(inner[1]) >= 2):
                    self._conversation = [inner[1][0], inner[1][1]]
                if isinstance(inner, list) and len(inner) > 4 and inner[4]:
                    for segment in inner[4]:
                        if not (isinstance(segment, list) and len(segment) > 1):
                            continue
                        text = segment[1]
                        if isinstance(text, list) and len(text) > 0:
                            text = text[0]
                        if isinstance(text, str):
                            parts.append(text)
        content = _clean_repeated("".join(parts))
        if not content:
            raise ProviderError("gemini returned an empty completion")
        return Completion(content, self.default_model, self.name)

    async def complete(self, request: ChatRequest, model: str | None = None) -> Completion:
        # Stateless: each request starts a fresh anonymous conversation.
        self._conversation = [None, None]
        message = _last_user_message(request)
        query = (
            f"?bl=boq_assistant-bard-web-server_20260904.05_p0"
            f"&f.sid=-{int(time.time() * 1000) % 100000000}"
            f"&hl=en-US&_reqid={int(time.time() * 10000) % 10000000}&rt=c"
        )
        inner_request = [[message, 0, None, None, None, None, 0], ["en-US"], self._conversation]
        body = {"f.req": json.dumps([None, json.dumps(inner_request)])}
        last_error: Exception | None = None
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(headers=self._headers(), timeout=90, follow_redirects=True) as client:
                    await client.get(self._BASE, timeout=30)
                    response = await client.post(self._BASE + self._ENDPOINT + query, data=body)
                response.raise_for_status()
                completion = self._extract(response.text)
                if completion.content:
                    return completion
                last_error = ProviderError("gemini returned an empty completion")
            except (httpx.HTTPError, ValueError) as error:
                last_error = error
            await asyncio.sleep(0.5 * (attempt + 1))
        raise ProviderError(f"gemini failed: {last_error}") from last_error


def _free_api_key_provider_classes() -> list[type[Provider]]:
    return [
        GroqProvider,
        OpenRouterProvider,
        MistralProvider,
        CloudflareProvider,
    ]


def configured_providers() -> list[Provider]:
    """Providers enabled without a survey.

    Gemini, Kilo's anonymous gateway, opencode's Zen free tier, OVHcloud's
    anonymous endpoints, and LLM7's anonymous turbo tier are always available
    (no login, no key). The free-tier API-key providers are only enabled when
    their environment variable is set, so the router can fall back to them if
    the anonymous providers are throttled or blocked.
    """
    providers: list[Provider] = [GeminiProvider(), KiloProvider(), ZenProvider(), OVHProvider(), LLM7Provider()]
    for provider_cls in _free_api_key_provider_classes():
        instance = provider_cls()
        if instance.api_key:
            providers.append(instance)
    return providers


def sorted_providers(providers: list[Provider]) -> list[Provider]:
    """Order a list of providers from smartest to weakest fallback."""
    return sorted(providers, key=lambda p: p.smartness, reverse=True)


@dataclass(frozen=True)
class ProbeResult:
    name: str
    alive: bool
    latency_ms: float
    model: str
    error: str


async def probe_providers(providers: list[Provider]) -> list[ProbeResult]:
    """Probe all providers concurrently and return results sorted by smartness descending."""
    async def _probe_one(provider: Provider) -> ProbeResult:
        alive, latency_ms, model, error = await provider.probe()
        return ProbeResult(provider.name, alive, latency_ms, model, error)
    results = await asyncio.gather(*[_probe_one(p) for p in providers])
    return sorted(results, key=lambda r: next(p.smartness for p in providers if p.name == r.name), reverse=True)
