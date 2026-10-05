# Provider Status Report

_Generated: 2026-10-05 13:17:45 UTC_

## Resident Providers

| Provider | Alive | HTTP | Latency | Model | Error |
|----------|-------|------|---------|-------|-------|
| gemini | ✅ | 200 | 4106ms | gemini-2.5-flash |  |
| kilo | ❌ | 404 | 244ms |  | {"error":"The requested model 'minimax/minimax-m3:free' does not exist. Please u |
| zen | ❌ | 403 | 210ms |  | {"type":"error","error":{"type":"FreeTierError","message":"Error from provider ( |
| ovh | ❌ | 429 | 1038ms |  | {
  "message":"API rate limit exceeded",
  "request_id":"f784d300b674497818afd83 |
| llm7 | ✅ | 200 | 5625ms | minimax-m2.7 |  |

> **⚠ 3 resident provider(s) are dead:** kilo, zen, ovh


## Candidate Endpoints

| Provider | Alive | HTTP | Latency | Model | Note |
|----------|-------|------|---------|-------|------|
| aihorde | ❌ | 200 | 493ms |  | alive for images only |
| ollama-cloud | ❌ | 401 | 154ms |  | requires API key |
| pollinations | ❌ | 200 | 535ms |  |  |
| perplexity | ❌ | 403 | 77ms |  | Cloudflare-gated |

## Summary

- Resident alive: **2/5**
- Candidates tested: **4**
- New anonymous providers found: **0**
