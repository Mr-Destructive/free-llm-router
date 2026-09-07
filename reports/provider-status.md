# Provider Status Report

_Generated: 2026-09-07 11:18:09 UTC_

## Resident Providers

| Provider | Alive | HTTP | Latency | Model | Error |
|----------|-------|------|---------|-------|-------|
| gemini | ✅ | 200 | 3151ms | gemini-2.5-flash |  |
| kilo | ✅ | 200 | 1079ms | minimax/minimax-m3:free |  |
| zen | ❌ | 400 | 363ms |  | {"type":"error","error":{"type":"MissingSessionID","message":"Error from provide |
| ovh | ✅ | 200 | 1256ms | gpt-oss-20b |  |
| llm7 | ✅ | 200 | 1942ms | minimax-m2.7 |  |

> **⚠ 1 resident provider(s) are dead:** zen


## Candidate Endpoints

| Provider | Alive | HTTP | Latency | Model | Note |
|----------|-------|------|---------|-------|------|
| aihorde | ❌ | 200 | 379ms |  | alive for images only |
| ollama-cloud | ❌ | 401 | 93ms |  | requires API key |
| pollinations | ❌ | 200 | 445ms |  |  |
| perplexity | ❌ | 403 | 60ms |  | Cloudflare-gated |

## Summary

- Resident alive: **4/5**
- Candidates tested: **4**
- New anonymous providers found: **0**
