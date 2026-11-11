
import os

import httpx
from fastapi import FastAPI, HTTPException, Request

app = FastAPI(title="Gemini Compatibility Proxy")

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY environment variable is not set",
        )

    payload = await request.json()

    # Gemini does not accept the OpenAI "store" field.
    payload.pop("store", None)

    print("REQUEST SUMMARY", flush=True)
    print("Model:", payload.get("model"), flush=True)
    print("Top-level fields:", list(payload.keys()), flush=True)

    for message in payload.get("messages", []):
        content = message.get("content", "")
        print(
            f"Message role={message.get('role')}, "
            f"content length={len(str(content))}, "
            f"preview={str(content)[:150]!r}",
            flush=True,
        )

    print("Tools:", len(payload.get("tools", [])), flush=True)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                GEMINI_API_URL,
                json=payload,
                headers=headers,
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=502,
                detail="Could not connect to the Gemini API",
            )

    if response.is_error:
        print("GEMINI UPSTREAM ERROR", flush=True)
        print("Status:", response.status_code, flush=True)
        print("Response:", response.text[:2000], flush=True)

        raise HTTPException(
            status_code=response.status_code,
            detail={
                "message": "Gemini API returned an error",
                "gemini_response": response.text,
            },
        )

    try:
        return response.json()
    except ValueError:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Gemini returned a non-JSON response",
                "status_code": response.status_code,
                "response_text": response.text,
            },
        )
