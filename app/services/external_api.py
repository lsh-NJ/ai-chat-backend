import httpx
from fastapi import HTTPException
from app.core.config import settings


def fetch_github_status() -> dict:
    url = "https://api.github.com"

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai-chat-backend/0.1",
    }

    try:
        with httpx.Client(
            proxy=settings.proxy_url,
            headers=headers,
            timeout=10.0,
        ) as client:
            response = client.get(url)

        response.raise_for_status()
        return response.json()

    except httpx.TimeoutException as e:
        raise HTTPException(
            status_code=504,
            detail="External API request timeout",
        ) from e

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"External API returned bad status code: {e.response.text[:200]}",
        ) from e

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail=f"External API request failed: {type(e).__name__}",
        ) from e