# Provider Status Report

_Generated: 2026-11-16 14:30:35 UTC_

## Resident Providers

| Provider | Alive | HTTP | Latency | Model | Error |
|----------|-------|------|---------|-------|-------|
| gemini | ✅ | 200 | 4317ms | gemini-2.5-flash |  |
| kilo | ❌ | 404 | 638ms |  | {"error":"The requested model 'minimax/minimax-m3:free' does not exist. Please u |
| zen | ❌ | 429 | 152ms |  | {"type":"error","error":{"type":"FreeUsageLimitError","message":"Free usage limi |
| ovh | ✅ | 200 | 1402ms | gpt-oss-20b |  |
| llm7 | ✅ | 200 | 8243ms | minimax-m2.7 |  |

> **⚠ 2 resident provider(s) are dead:** kilo, zen


## Candidate Endpoints

| Provider | Alive | HTTP | Latency | Model | Note |
|----------|-------|------|---------|-------|------|
| aihorde | ❌ | 200 | 419ms |  | alive for images only |
| ollama-cloud | ❌ | 401 | 130ms |  | requires API key |
| pollinations | ❌ | 200 | 598ms |  |  |
| perplexity | ❌ | 403 | 38ms |  | Cloudflare-gated |

## Summary

- Resident alive: **3/5**
- Candidates tested: **4**
- New anonymous providers found: **0**
