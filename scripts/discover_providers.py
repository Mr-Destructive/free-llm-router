#!/usr/bin/env python3
"""Probe all known anonymous LLM providers and produce a status report.

Probes the five resident providers (gemini, kilo, zen, ovh, llm7) plus
candidate endpoints that are *not* yet resident, writes
``reports/provider-status.json`` and ``reports/provider-status.md``, and
exits with code 1 when any resident provider is dead (so CI can surface it).

Usage:
    python scripts/discover_providers.py
    python scripts/discover_providers.py --json-only   # skip markdown
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = REPO_ROOT / "reports"

RESIDENT_NAMES = {"gemini", "kilo", "zen", "ovh", "llm7"}


# ---------------------------------------------------------------------------
# Candidate endpoints not yet wired into the router as providers.
# Each entry can be:
#   {"name", "type": "openai", "url", "model"}              – OpenAI-compatible
#   {"name", "type": "gemini-web"}                          – Gemini web RPC
#   {"name", "type": "pollinations"}                        – Pollinations GET
# ---------------------------------------------------------------------------

CANDIDATES: list[dict[str, str]] = [
    # Gemini web (already resident, but listed for completeness)
    {"name": "gemini", "type": "gemini-web"},
    # Kilo
    {"name": "kilo", "type": "openai", "url": "https://api.kilo.ai/api/gateway/v1/chat/completions", "model": "minimax/minimax-m3:free"},
    # Zen
    {"name": "zen", "type": "openai", "url": "https://opencode.ai/zen/v1/chat/completions", "model": "big-pickle"},
    # OVH
    {"name": "ovh", "type": "openai", "url": "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/chat/completions", "model": "gpt-oss-20b"},
    # LLM7
    {"name": "llm7", "type": "openai", "url": "https://api.llm7.io/v1/chat/completions", "model": "minimax-m2.7"},
    # Candidates (not yet resident)
    {"name": "aihorde", "type": "aihorde", "note": "crowdsourced, slow, no text models currently"},
    {"name": "ollama-cloud", "type": "openai", "url": "https://ollama.com/v1/chat/completions", "model": "gemma3:1b", "note": "requires API key"},
    {"name": "pollinations", "type": "pollinations", "note": "text API returns 402"},
    {"name": "perplexity", "type": "openai", "url": "https://www.perplexity.ai/backend-api/chat/completions", "model": "sonar", "note": "Cloudflare-gated"},
]

PROMPT = "What is 2+2? Reply with just the number."
TIMEOUT = 60


@dataclass
class ProbeOutcome:
    name: str
    alive: bool
    http_code: int = 0
    latency_ms: float = 0.0
    model: str = ""
    error: str = ""
    note: str = ""


async def _probe_openai(url: str, model: str) -> ProbeOutcome:
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            resp = await client.post(
                url,
                json={"model": model, "messages": [{"role": "user", "content": PROMPT}], "max_tokens": 20},
                headers={"Content-Type": "application/json"},
            )
        latency = (time.monotonic() - start) * 1000
        if resp.status_code >= 400:
            return ProbeOutcome(name="", alive=False, http_code=resp.status_code, latency_ms=latency, error=resp.text[:200])
        data = resp.json()
        content = ""
        choices = data.get("choices") or []
        if choices:
            msg = choices[0].get("message") or {}
            content = msg.get("content") or msg.get("reasoning") or ""
        return ProbeOutcome(name="", alive=bool(content), http_code=resp.status_code, latency_ms=latency, model=data.get("model", model))
    except Exception as exc:
        latency = (time.monotonic() - start) * 1000
        return ProbeOutcome(name="", alive=False, latency_ms=latency, error=str(exc)[:200])


async def _probe_gemini_web() -> ProbeOutcome:
    """Use the GeminiProvider class from the package."""
    try:
        from free_llm_router.providers import GeminiProvider
        start = time.monotonic()
        provider = GeminiProvider()
        from free_llm_router.models import ChatRequest
        req = ChatRequest(messages=[{"role": "user", "content": PROMPT}], max_tokens=20)
        completion = await provider.complete(req)
        latency = (time.monotonic() - start) * 1000
        return ProbeOutcome(name="gemini", alive=True, http_code=200, latency_ms=latency, model=completion.model)
    except Exception as exc:
        latency = (time.monotonic() - start) * 1000
        return ProbeOutcome(name="gemini", alive=False, latency_ms=latency, error=str(exc)[:200])


async def _probe_aihorde() -> ProbeOutcome:
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            resp = await client.get("https://aihorde.net/api/v2/status/models", headers={"apikey": "0000000000"})
        latency = (time.monotonic() - start) * 1000
        models = resp.json()
        text_models = [m for m in models if m.get("type") == "text" and m.get("count", 0) > 0]
        if not text_models:
            return ProbeOutcome(name="aihorde", alive=False, http_code=resp.status_code, latency_ms=latency, error="no text models available", note="alive for images only")
        return ProbeOutcome(name="aihorde", alive=True, http_code=resp.status_code, latency_ms=latency, model=f"{len(text_models)} text models")
    except Exception as exc:
        latency = (time.monotonic() - start) * 1000
        return ProbeOutcome(name="aihorde", alive=False, latency_ms=latency, error=str(exc)[:200])


async def _probe_pollinations() -> ProbeOutcome:
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get("https://text.pollinations.ai/openai", params={"message": PROMPT})
        latency = (time.monotonic() - start) * 1000
        return ProbeOutcome(name="pollinations", alive=False, http_code=resp.status_code, latency_ms=latency, error=f"HTTP {resp.status_code}")
    except Exception as exc:
        latency = (time.monotonic() - start) * 1000
        return ProbeOutcome(name="pollinations", alive=False, latency_ms=latency, error=str(exc)[:200])


async def _probe_candidate(cand: dict[str, str]) -> ProbeOutcome:
    name = cand["name"]
    probe_type = cand["type"]
    if probe_type == "openai":
        outcome = await _probe_openai(cand["url"], cand["model"])
        outcome.name = name
        outcome.note = cand.get("note", "")
        return outcome
    if probe_type == "gemini-web":
        return await _probe_gemini_web()
    if probe_type == "aihorde":
        return await _probe_aihorde()
    if probe_type == "pollinations":
        return await _probe_pollinations()
    return ProbeOutcome(name=name, alive=False, error=f"unknown probe type: {probe_type}")


def _build_markdown(outcomes: list[ProbeOutcome]) -> str:
    lines: list[str] = []
    lines.append("# Provider Status Report\n")
    lines.append(f"_Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}_\n")

    resident = [o for o in outcomes if o.name in RESIDENT_NAMES]
    candidates = [o for o in outcomes if o.name not in RESIDENT_NAMES]

    lines.append("## Resident Providers\n")
    lines.append("| Provider | Alive | HTTP | Latency | Model | Error |")
    lines.append("|----------|-------|------|---------|-------|-------|")
    for o in resident:
        status = "✅" if o.alive else "❌"
        lines.append(f"| {o.name} | {status} | {o.http_code} | {o.latency_ms:.0f}ms | {o.model} | {o.error[:80]} |")

    dead_resident = [o for o in resident if not o.alive]
    if dead_resident:
        lines.append(f"\n> **⚠ {len(dead_resident)} resident provider(s) are dead:** {', '.join(o.name for o in dead_resident)}\n")

    if candidates:
        lines.append("\n## Candidate Endpoints\n")
        lines.append("| Provider | Alive | HTTP | Latency | Model | Note |")
        lines.append("|----------|-------|------|---------|-------|------|")
        for o in candidates:
            status = "✅" if o.alive else "❌"
            lines.append(f"| {o.name} | {status} | {o.http_code} | {o.latency_ms:.0f}ms | {o.model} | {o.note} |")

    new_alive = [o for o in candidates if o.alive]
    if new_alive:
        lines.append(f"\n> **🎉 {len(new_alive)} new anonymous provider(s) found:** {', '.join(o.name for o in new_alive)}\n")

    lines.append("\n## Summary\n")
    alive_count = sum(1 for o in resident if o.alive)
    lines.append(f"- Resident alive: **{alive_count}/{len(resident)}**")
    lines.append(f"- Candidates tested: **{len(candidates)}**")
    alive_candidates = [o for o in candidates if o.alive]
    lines.append(f"- New anonymous providers found: **{len(alive_candidates)}**")
    return "\n".join(lines) + "\n"


async def run(json_only: bool = False) -> int:
    outcomes = []
    for cand in CANDIDATES:
        outcome = await _probe_candidate(cand)
        outcomes.append(outcome)
        status = "OK" if outcome.alive else "FAIL"
        print(f"  [{status:>4}] {outcome.name:<15} {outcome.latency_ms:>7.0f}ms  {outcome.model or outcome.error[:60]}")

    REPORT_DIR.mkdir(exist_ok=True)

    json_path = REPORT_DIR / "provider-status.json"
    json_path.write_text(json.dumps([asdict(o) for o in outcomes], indent=2))
    print(f"\n  JSON report: {json_path}")

    if not json_only:
        md_path = REPORT_DIR / "provider-status.md"
        md_path.write_text(_build_markdown(outcomes))
        print(f"  MD report:   {md_path}")

    dead_resident = [o for o in outcomes if o.name in RESIDENT_NAMES and not o.alive]
    if dead_resident:
        print(f"\n  ⚠ DEAD resident providers: {', '.join(o.name for o in dead_resident)}")
        return 1
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe anonymous LLM providers and generate status report")
    parser.add_argument("--json-only", action="store_true", help="Skip markdown report")
    args = parser.parse_args()
    exit_code = asyncio.run(run(json_only=args.json_only))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
