# Provider Status Report

_Generated: 2026-10-26 12:04:29 UTC_

## Resident Providers

| Provider | Alive | HTTP | Latency | Model | Error |
|----------|-------|------|---------|-------|-------|
| gemini | ✅ | 200 | 44840ms | gemini-2.5-flash |  |
| kilo | ❌ | 404 | 749ms |  | {"error":"The requested model 'minimax/minimax-m3:free' does not exist. Please u |
| zen | ❌ | 429 | 50ms |  | {"type":"error","error":{"type":"FreeUsageLimitError","message":"Free usage limi |
| ovh | ✅ | 200 | 1189ms | gpt-oss-20b |  |
| llm7 | ✅ | 200 | 1517ms | minimax-m2.7 |  |

> **⚠ 2 resident provider(s) are dead:** kilo, zen


## Candidate Endpoints

| Provider | Alive | HTTP | Latency | Model | Note |
|----------|-------|------|---------|-------|------|
| aihorde | ❌ | 200 | 392ms |  | alive for images only |
| ollama-cloud | ❌ | 401 | 46ms |  | requires API key |
| pollinations | ❌ | 200 | 380ms |  |  |
| perplexity | ❌ | 403 | 41ms |  | Cloudflare-gated |

## Summary

- Resident alive: **3/5**
- Candidates tested: **4**
- New anonymous providers found: **0**
