import httpx
from fastapi import HTTPException

from app.core.config import settings


def call_llm(messages: list[dict[str, str]]) -> str:
    if not settings.deepseek_api_key:
        raise HTTPException(
            status_code=500,
            detail="DeepSeek API key is not configured",
        )

    base_url = settings.deepseek_base_url.rstrip("/")
    url = f"{base_url}/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "model": settings.deepseek_model,
        "messages": [
            {
                "role": "system",
                "content": "你是一个简洁、友好、可靠的 AI 助手。",
            },
            *messages,
        ],
        "temperature": 0.7,
        "thinking": {
            "type": "disabled",
        },
    }

    try:
        with httpx.Client(
            timeout=60.0,
        ) as client:
            response = client.post(
                url,
                headers=headers,
                json=payload,
            )

        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]

    except httpx.TimeoutException as e:
        raise HTTPException(
            status_code=504,
            detail="LLM request timeout",
        ) from e

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail={
                "message": "LLM API returned bad status code",
                "status_code": e.response.status_code,
                "response_text": e.response.text[:500],
                "url": str(e.request.url),
                "method": e.request.method,
                "model": settings.deepseek_model,
            },
        ) from e

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail=f"LLM API request failed: {type(e).__name__}",
        ) from e

    except KeyError as e:
        raise HTTPException(
            status_code=502,
            detail="Unexpected LLM API response format",
        ) from e