# Provider Status Report

_Generated: 2026-09-14 11:27:56 UTC_

## Resident Providers

| Provider | Alive | HTTP | Latency | Model | Error |
|----------|-------|------|---------|-------|-------|
| gemini | ✅ | 200 | 4158ms | gemini-2.5-flash |  |
| kilo | ❌ | 404 | 183ms |  | {"error":"The requested model 'minimax/minimax-m3:free' does not exist. Please u |
| zen | ❌ | 400 | 226ms |  | {"type":"error","error":{"type":"MissingSessionID","message":"Error from provide |
| ovh | ❌ | 429 | 1463ms |  | {
  "message":"API rate limit exceeded",
  "request_id":"af6974625d690e233890c93 |
| llm7 | ✅ | 200 | 5021ms | minimax-m2.7 |  |

> **⚠ 3 resident provider(s) are dead:** kilo, zen, ovh


## Candidate Endpoints

| Provider | Alive | HTTP | Latency | Model | Note |
|----------|-------|------|---------|-------|------|
| aihorde | ❌ | 200 | 499ms |  | alive for images only |
| ollama-cloud | ❌ | 401 | 155ms |  | requires API key |
| pollinations | ❌ | 200 | 575ms |  |  |
| perplexity | ❌ | 403 | 71ms |  | Cloudflare-gated |

## Summary

- Resident alive: **2/5**
- Candidates tested: **4**
- New anonymous providers found: **0**
