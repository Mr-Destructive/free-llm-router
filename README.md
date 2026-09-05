# free-llm-router

An OpenAI-compatible gateway that routes chat requests to free cloud LLMs without
charging you or requiring a paid API subscription. It accepts OpenAI-compatible
chat requests and answers from whatever free provider is available, smartest
model first.

## Quick start

```bash
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/free-llm-router
```

The server listens on `http://127.0.0.1:8787`. Five anonymous providers are
enabled by default and need **no login and no API key**:

- **Gemini** — Google's anonymous web endpoint
- **Kilo** — Kilo.ai's gateway (`api.kilo.ai/api/gateway`, OpenAI-compatible),
  which serves OpenRouter-style `:free` models anonymously (e.g.
  `minimax/minimax-m3:free`, `poolside/laguna-s-2.1:free`) with automatic
  per-model failover.
- **Zen** — opencode's free tier (`opencode.ai/zen/v1`, `Bearer public`), which
  exposes multiple free models (`big-pickle`, `mimo-v2.5-free`,
  `nemotron-3.5-lightning-free`) with automatic per-model failover.
- **OVH** — OVHcloud AI Endpoints' anonymous tier (`oai.endpoints.kepler.ai.cloud.ovh.net`,
  OpenAI-compatible; shared pool rate-limited to roughly 2 RPM per model, so it
  sits low in the fallback order and tries `gpt-oss-20b` → `gpt-oss-120b` →
  `Qwen3-32B` → `Qwen3.5-9B`).
- **LLM7** — LLM7.io's anonymous `turbo` tier (`api.llm7.io/v1`,
  OpenAI-compatible; no signup), trying `minimax-m2.7` → `gpt-oss` →
  `mistral-Nemo-Instruct-2407` → `codestral-latest`.

```bash
curl http://127.0.0.1:8787/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"auto", "messages":[{"role":"user","content":"Explain Python generators."}]}'
```

Use it with the OpenAI SDK:

```python
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:8787/v1", api_key="not-used")
reply = client.chat.completions.create(
    model="auto", messages=[{"role": "user", "content": "Hello"}]
)
print(reply.choices[0].message.content)
```

## Providers

| Provider | Auth needed | How it works | Enabled by default |
|---|---|---|---|
| **Gemini** (smartest) | None | Reverses the anonymous browser handshake of `gemini.google.com` (the `_reqid`/`f.sid` query params plus the `x-goog-ext-*` JSPB headers with fresh random UUIDs). No API key, no login, no cookies. | ✅ Yes |
| **Kilo** | None | OpenAI-compatible gateway at `api.kilo.ai/api/gateway/v1`, serving OpenRouter-style `:free` models (`minimax/minimax-m3:free`, `poolside/laguna-s-2.1:free`, tensor/ultra from Nvidia…) with no API key. Each model is a separate, often busy quota bucket, so the provider fails over between them. | ✅ Yes |
| **Zen** (opencode free tier) | None | OpenAI-compatible endpoint at `opencode.ai/zen/v1` presented as `Bearer public` with opencode's User-Agent. Tries several free models and fails over between them. | ✅ Yes |
| **OVH** | None | OVHcloud AI Endpoints' anonymous tier at `oai.endpoints.kepler.ai.cloud.ovh.net` (OpenAI-compatible). Shared free pool, ~2 RPM per model, many 429s; used as a low-priority fallback. | ✅ Yes |
| **LLM7** | None | LLM7.io's anonymous `turbo` tier at `api.llm7.io/v1` (OpenAI-compatible, no signup). Per-model rate limits; fails over across its free models. | ✅ Yes |
| Groq | Free API key (`GROQ_API_KEY`) | Official OpenAI-compatible free tier | Via env key |
| OpenRouter | Free API key (`OPENROUTER_API_KEY`) | `:free` model endpoints | Via env key |
| Mistral | Free API key (`MISTRAL_API_KEY`) | Experiment tier | Via env key |
| Cloudflare | Free API token (`CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`) | Workers AI free tier | Via env key |

The router tries providers from **smartest to weakest**. Set an env key to opt a
provider in as a fallback:

```bash
export GROQ_API_KEY=...
export OPENROUTER_API_KEY=...
.venv/bin/free-llm-router
```

## Model routing

- `model: "auto"` — try every enabled provider from smartest to weakest.
- `model: "provider:model"` — use one provider (and optionally a specific model).
- `GET /v1/models` and `GET /healthz` show what is enabled.
- `stream: true` returns valid OpenAI Server-Sent Events.
- `POST /v1/chat/completions`, `GET /v1/models`, `GET /healthz` are the full API.

## How the Gemini adapter works

The `gemini.google.com` web app calls an undocumented streaming RPC:

```
POST /_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate
```

That endpoint works for logged-out visitors when the browser handshake is
repeated exactly: the `bl` build id, a fresh `f.sid` and `_reqid` in the query
string, browser `User-Agent`, and the `x-goog-ext-*` JSPB headers carrying newly
generated UUIDs. No authentication is ever sent. The `Freq` form body carries the
prompt; responses come back as Google's `)]}'`-prefixed framed JSON, which the
adapter parses, dedupes Gemini's repeated streamed segments, and cleans the
code-runner annotation blocks.

This is a private, undocumented endpoint: Google can change or restrict it
without notice, and it is used for personal automation. If Gemini is throttled
or blocked, the API-key providers kick in automatically.

## Limits

- Gemini's anonymous path is undocumented. The build id (`boq_...`) and response
  framing can change; the adapter pins the current one and retries transient
  failures twice.
- opencode's Zen free tier is per-model rate-limited and some models are
  occasionally busy; the router fails over between the free models automatically.
- Kilo's `:free` models, OVH's anonymous pool, and LLM7's turbo tier are all
  shared: expect 429s and transient 503s under load. Each provider exhausts its
  own model list before giving up, and the router then moves to the next
  provider.
- ChatGPT and Meta AI have no anonymous no-login endpoint — both gate anonymous
  visitors behind login/anti-bot challenges — so they are **not** adapter
  candidates here and are intentionally not included.
- "Free" means no paid subscription. Groq/OpenRouter/Mistral/Cloudflare still
  expect a free API-key signup; Gemini, Kilo, Zen, OVH and LLM7 alone need
  nothing.

## Health checks & provider discovery

Each provider exposes a lightweight `probe()` that sends a "What is 2+2?" prompt
and reports whether it is alive, its latency, and the model it answered with.
`probe_providers()` runs all configured providers concurrently:

```python
from free_llm_router.providers import configured_providers, probe_providers
import asyncio

results = asyncio.run(probe_providers(configured_providers()))
for r in results:
    print(f"{r.name}: {'OK' if r.alive else 'DEAD'} ({r.latency_ms:.0f}ms)")
```

### Discovery script

`scripts/discover_providers.py` probes every resident provider plus candidate
anonymous endpoints (AI Horde, Ollama Cloud, Pollinations, Perplexity, ...) and
writes `reports/provider-status.json` and `reports/provider-status.md`. It exits
with code 1 if any resident provider is dead.

```bash
python scripts/discover_providers.py
```

A GitHub Actions workflow (`.github/workflows/discover.yml`) runs this every
Monday on a cron schedule (and can be triggered manually via
*wokflow_dispatch*), committing the refreshed report to the repo so you always
have an up-to-date record and are alerted when a resident provider breaks or a
new anonymous endpoint shows up.