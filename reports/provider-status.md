# Provider Status Report

_Generated: 2026-11-23 17:06:23 UTC_

## Resident Providers

| Provider | Alive | HTTP | Latency | Model | Error |
|----------|-------|------|---------|-------|-------|
| gemini | ✅ | 200 | 112523ms | gemini-2.5-flash |  |
| kilo | ❌ | 404 | 681ms |  | {"error":"The requested model 'minimax/minimax-m3:free' does not exist. Please u |
| zen | ❌ | 429 | 69ms |  | {"type":"error","error":{"type":"FreeUsageLimitError","message":"Free usage limi |
| ovh | ❌ | 429 | 467ms |  | {
  "message":"API rate limit exceeded",
  "request_id":"b6e4c563641de667b2f0cb4 |
| llm7 | ✅ | 200 | 37779ms | minimax-m2.7 |  |

> **⚠ 3 resident provider(s) are dead:** kilo, zen, ovh


## Candidate Endpoints

| Provider | Alive | HTTP | Latency | Model | Note |
|----------|-------|------|---------|-------|------|
| aihorde | ❌ | 200 | 1071ms |  | alive for images only |
| ollama-cloud | ❌ | 401 | 44ms |  | requires API key |
| pollinations | ❌ | 200 | 406ms |  |  |
| perplexity | ❌ | 403 | 23ms |  | Cloudflare-gated |

## Summary

- Resident alive: **2/5**
- Candidates tested: **4**
- New anonymous providers found: **0**
