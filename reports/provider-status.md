# Provider Status Report

_Generated: 2026-09-21 11:42:50 UTC_

## Resident Providers

| Provider | Alive | HTTP | Latency | Model | Error |
|----------|-------|------|---------|-------|-------|
| gemini | ✅ | 200 | 4172ms | gemini-2.5-flash |  |
| kilo | ❌ | 403 | 60ms |  | {"error":{"code":"403","message":"Forbidden","id":"sfo1::qxhlk-1789990907697-e62 |
| zen | ❌ | 403 | 205ms |  | {"type":"error","error":{"type":"FreeTierError","message":"Error from provider ( |
| ovh | ❌ | 429 | 940ms |  | {
  "message":"API rate limit exceeded",
  "request_id":"3a12a232c68f654b9128541 |
| llm7 | ❌ | 0 | 60102ms |  |  |

> **⚠ 4 resident provider(s) are dead:** kilo, zen, ovh, llm7


## Candidate Endpoints

| Provider | Alive | HTTP | Latency | Model | Note |
|----------|-------|------|---------|-------|------|
| aihorde | ❌ | 200 | 508ms |  | alive for images only |
| ollama-cloud | ❌ | 401 | 134ms |  | requires API key |
| pollinations | ❌ | 200 | 502ms |  |  |
| perplexity | ❌ | 403 | 42ms |  | Cloudflare-gated |

## Summary

- Resident alive: **1/5**
- Candidates tested: **4**
- New anonymous providers found: **0**
