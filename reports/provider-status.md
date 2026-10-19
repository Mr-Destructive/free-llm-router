# Provider Status Report

_Generated: 2026-10-19 11:48:48 UTC_

## Resident Providers

| Provider | Alive | HTTP | Latency | Model | Error |
|----------|-------|------|---------|-------|-------|
| gemini | ✅ | 200 | 21220ms | gemini-2.5-flash |  |
| kilo | ❌ | 404 | 579ms |  | {"error":"The requested model 'minimax/minimax-m3:free' does not exist. Please u |
| zen | ❌ | 403 | 150ms |  | {"type":"error","error":{"type":"FreeTierError","message":"OpenCode's free tier  |
| ovh | ✅ | 200 | 1496ms | gpt-oss-20b |  |
| llm7 | ✅ | 200 | 1839ms | minimax-m2.7 |  |

> **⚠ 2 resident provider(s) are dead:** kilo, zen


## Candidate Endpoints

| Provider | Alive | HTTP | Latency | Model | Note |
|----------|-------|------|---------|-------|------|
| aihorde | ❌ | 200 | 315ms |  | alive for images only |
| ollama-cloud | ❌ | 401 | 139ms |  | requires API key |
| pollinations | ❌ | 200 | 538ms |  |  |
| perplexity | ❌ | 403 | 85ms |  | Cloudflare-gated |

## Summary

- Resident alive: **3/5**
- Candidates tested: **4**
- New anonymous providers found: **0**
