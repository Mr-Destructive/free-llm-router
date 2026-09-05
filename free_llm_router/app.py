from __future__ import annotations

import json
import time
import uuid
from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse

from .models import ChatRequest
from .providers import Completion, configured_providers
from .router import LLMRouter, NoProviderAvailable


def _completion_payload(completion: Completion, request: ChatRequest) -> dict:
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": completion.model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": completion.content},
            "finish_reason": "stop",
        }],
        "free_llm_router": {"provider": completion.provider},
    }


async def _sse(payload: dict) -> AsyncIterator[str]:
    chunk = {
        "id": payload["id"], "object": "chat.completion.chunk", "created": payload["created"],
        "model": payload["model"],
        "choices": [{"index": 0, "delta": {"role": "assistant", "content": payload["choices"][0]["message"]["content"]}, "finish_reason": None}],
    }
    yield f"data: {json.dumps(chunk)}\n\n"
    chunk["choices"][0] = {"index": 0, "delta": {}, "finish_reason": "stop"}
    yield f"data: {json.dumps(chunk)}\n\n"
    yield "data: [DONE]\n\n"


def create_app(router: LLMRouter | None = None) -> FastAPI:
    app = FastAPI(title="free-llm-router", version="0.1.0")
    app.state.router = router or LLMRouter(configured_providers())

    @app.get("/healthz")
    async def healthz() -> dict:
        return {"ok": True, "providers": [provider.name for provider in app.state.router.providers]}

    @app.get("/v1/models")
    async def models() -> dict:
        return {"object": "list", "data": [
            {"id": "auto", "object": "model", "owned_by": "free-llm-router"},
            *({"id": f"{provider.name}:{provider.default_model}", "object": "model", "owned_by": provider.name} for provider in app.state.router.providers),
        ]}

    @app.post("/v1/chat/completions")
    async def chat_completions(request: ChatRequest):
        try:
            completion = await app.state.router.complete(request)
        except NoProviderAvailable as error:
            raise HTTPException(status_code=503, detail=str(error)) from error
        payload = _completion_payload(completion, request)
        if request.stream:
            return StreamingResponse(_sse(payload), media_type="text/event-stream")
        return JSONResponse(payload)

    return app


app = create_app()

