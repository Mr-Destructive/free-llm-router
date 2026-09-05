# Provider Status Report

_Generated: 2026-09-05 12:04:41 UTC_

## Resident Providers

| Provider | Alive | HTTP | Latency | Model | Error |
|----------|-------|------|---------|-------|-------|
| gemini | ✅ | 200 | 7900ms | gemini-2.5-flash |  |
| kilo | ❌ | 429 | 503ms |  | {"error":{"message":"Rate limit exceeded: minimax/minimax-m3-20260531/3e7a48d4-5 |
| zen | ❌ | 429 | 1023ms |  | {"type":"error","error":{"type":"FreeUsageLimitError","message":"Error from prov |
| ovh | ❌ | 429 | 616ms |  | {
  "message":"API rate limit exceeded",
  "request_id":"0670373b55cf9e3d0210a03 |
| llm7 | ✅ | 200 | 615ms | minimax-m2.7 |  |

> **⚠ 3 resident provider(s) are dead:** kilo, zen, ovh


## Candidate Endpoints

| Provider | Alive | HTTP | Latency | Model | Note |
|----------|-------|------|---------|-------|------|
| aihorde | ❌ | 200 | 554ms |  | alive for images only |
| ollama-cloud | ❌ | 401 | 365ms |  | requires API key |
| pollinations | ❌ | 200 | 717ms |  |  |
| perplexity | ❌ | 403 | 50ms |  | Cloudflare-gated |

## Summary

- Resident alive: **2/5**
- Candidates tested: **4**
- New anonymous providers found: **0**
