# Provider Status Report

_Generated: 2026-09-05 14:35:44 UTC_

## Resident Providers

| Provider | Alive | HTTP | Latency | Model | Error |
|----------|-------|------|---------|-------|-------|
| gemini | ✅ | 200 | 3392ms | gemini-2.5-flash |  |
| kilo | ✅ | 200 | 2748ms | minimax/minimax-m3:free |  |
| zen | ❌ | 200 | 6546ms | big-pickle |  |
| ovh | ❌ | 429 | 1031ms |  | {
  "message":"API rate limit exceeded",
  "request_id":"9125dd1890eeb60c25b1250 |
| llm7 | ✅ | 200 | 3361ms | minimax-m2.7 |  |

> **⚠ 2 resident provider(s) are dead:** zen, ovh


## Candidate Endpoints

| Provider | Alive | HTTP | Latency | Model | Note |
|----------|-------|------|---------|-------|------|
| aihorde | ❌ | 200 | 569ms |  | alive for images only |
| ollama-cloud | ❌ | 401 | 120ms |  | requires API key |
| pollinations | ❌ | 200 | 538ms |  |  |
| perplexity | ❌ | 403 | 94ms |  | Cloudflare-gated |

## Summary

- Resident alive: **3/5**
- Candidates tested: **4**
- New anonymous providers found: **0**
