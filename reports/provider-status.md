# Provider Status Report

_Generated: 2026-10-12 14:07:37 UTC_

## Resident Providers

| Provider | Alive | HTTP | Latency | Model | Error |
|----------|-------|------|---------|-------|-------|
| gemini | ✅ | 200 | 4008ms | gemini-2.5-flash |  |
| kilo | ❌ | 404 | 1004ms |  | {"error":"The requested model 'minimax/minimax-m3:free' does not exist. Please u |
| zen | ❌ | 403 | 167ms |  | {"type":"error","error":{"type":"FreeTierError","message":"OpenCode's free tier  |
| ovh | ✅ | 200 | 1213ms | gpt-oss-20b |  |
| llm7 | ❌ | 400 | 349ms |  | {"error":{"message":"Model 'minimax-m2.7' is currently unavailable.","type":"inv |

> **⚠ 3 resident provider(s) are dead:** kilo, zen, llm7


## Candidate Endpoints

| Provider | Alive | HTTP | Latency | Model | Note |
|----------|-------|------|---------|-------|------|
| aihorde | ❌ | 200 | 486ms |  | alive for images only |
| ollama-cloud | ❌ | 401 | 195ms |  | requires API key |
| pollinations | ❌ | 200 | 501ms |  |  |
| perplexity | ❌ | 403 | 41ms |  | Cloudflare-gated |

## Summary

- Resident alive: **2/5**
- Candidates tested: **4**
- New anonymous providers found: **0**
