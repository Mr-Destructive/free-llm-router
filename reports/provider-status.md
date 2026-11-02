# Provider Status Report

_Generated: 2026-11-02 14:29:43 UTC_

## Resident Providers

| Provider | Alive | HTTP | Latency | Model | Error |
|----------|-------|------|---------|-------|-------|
| gemini | ✅ | 200 | 7082ms | gemini-2.5-flash |  |
| kilo | ❌ | 404 | 790ms |  | {"error":"The requested model 'minimax/minimax-m3:free' does not exist. Please u |
| zen | ❌ | 429 | 158ms |  | {"type":"error","error":{"type":"FreeUsageLimitError","message":"Free usage limi |
| ovh | ✅ | 200 | 1932ms | gpt-oss-20b |  |
| llm7 | ✅ | 200 | 20365ms | minimax-m2.7 |  |

> **⚠ 2 resident provider(s) are dead:** kilo, zen


## Candidate Endpoints

| Provider | Alive | HTTP | Latency | Model | Note |
|----------|-------|------|---------|-------|------|
| aihorde | ❌ | 200 | 472ms |  | alive for images only |
| ollama-cloud | ❌ | 401 | 228ms |  | requires API key |
| pollinations | ❌ | 200 | 733ms |  |  |
| perplexity | ❌ | 403 | 328ms |  | Cloudflare-gated |

## Summary

- Resident alive: **3/5**
- Candidates tested: **4**
- New anonymous providers found: **0**
