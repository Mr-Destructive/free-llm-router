# Provider Status Report

_Generated: 2026-11-09 14:53:51 UTC_

## Resident Providers

| Provider | Alive | HTTP | Latency | Model | Error |
|----------|-------|------|---------|-------|-------|
| gemini | ✅ | 200 | 4645ms | gemini-2.5-flash |  |
| kilo | ❌ | 404 | 657ms |  | {"error":"The requested model 'minimax/minimax-m3:free' does not exist. Please u |
| zen | ❌ | 429 | 122ms |  | {"type":"error","error":{"type":"FreeUsageLimitError","message":"Free usage limi |
| ovh | ✅ | 200 | 3266ms | gpt-oss-20b |  |
| llm7 | ❌ | 400 | 217ms |  | {"error":{"message":"Model 'minimax-m2.7' is currently unavailable.","type":"inv |

> **⚠ 3 resident provider(s) are dead:** kilo, zen, llm7


## Candidate Endpoints

| Provider | Alive | HTTP | Latency | Model | Note |
|----------|-------|------|---------|-------|------|
| aihorde | ❌ | 200 | 421ms |  | alive for images only |
| ollama-cloud | ❌ | 401 | 132ms |  | requires API key |
| pollinations | ❌ | 200 | 643ms |  |  |
| perplexity | ❌ | 403 | 39ms |  | Cloudflare-gated |

## Summary

- Resident alive: **2/5**
- Candidates tested: **4**
- New anonymous providers found: **0**
