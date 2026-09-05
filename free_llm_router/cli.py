import uvicorn


def main() -> None:
    uvicorn.run("free_llm_router.app:app", host="127.0.0.1", port=8787)

