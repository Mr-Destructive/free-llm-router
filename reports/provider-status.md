# Provider Status Report

_Generated: 2026-09-28 12:41:46 UTC_

## Resident Providers

| Provider | Alive | HTTP | Latency | Model | Error |
|----------|-------|------|---------|-------|-------|
| gemini | ✅ | 200 | 281247ms | gemini-2.5-flash |  |
| kilo | ❌ | 404 | 413ms |  | {"error":"The requested model 'minimax/minimax-m3:free' does not exist. Please u |
| zen | ❌ | 403 | 307ms |  | {"type":"error","error":{"type":"FreeTierError","message":"Error from provider ( |
| ovh | ❌ | 429 | 1343ms |  | {
  "message":"API rate limit exceeded",
  "request_id":"36363f6b5cefeb397042552 |
| llm7 | ✅ | 200 | 3442ms | minimax-m2.7 |  |

> **⚠ 3 resident provider(s) are dead:** kilo, zen, ovh


## Candidate Endpoints

| Provider | Alive | HTTP | Latency | Model | Note |
|----------|-------|------|---------|-------|------|
| aihorde | ❌ | 200 | 380ms |  | alive for images only |
| ollama-cloud | ❌ | 401 | 303ms |  | requires API key |
| pollinations | ❌ | 200 | 664ms |  |  |
| perplexity | ❌ | 403 | 169ms |  | Cloudflare-gated |

## Summary

- Resident alive: **2/5**
- Candidates tested: **4**
- New anonymous providers found: **0**
