import httpx
import json
from collections.abc import Iterator
from fastapi import HTTPException
from app.core.config import settings

class LLMStreamError(Exception):
    """模型流式传输过程中发生错误。"""

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
    
# 流式输出
def stream_llm(
    messages: list[dict[str, str]],
) -> Iterator[str]:
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
        "Accept": "text/event-stream",
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
        "stream": True, # 告诉模型需要流式传输
    }

    timeout = httpx.Timeout(
        connect=10.0,
        read=120.0,
        write=30.0,
        pool=10.0,
    )

    client = httpx.Client(timeout=timeout)

    try:
        request = client.build_request(
            method="POST",
            url=url,
            headers=headers,
            json=payload,
        )

        response = client.send(
            request,
            stream=True, # 告诉 httpx 需要流式获取模型返回的数据
        )

        response.raise_for_status()

    except httpx.TimeoutException as e:
        client.close()

        raise HTTPException(
            status_code=504,
            detail="LLM stream request timeout",
        ) from e

    except httpx.HTTPStatusError as e:
        client.close()

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
        client.close()

        raise HTTPException(
            status_code=502,
            detail=f"LLM API request failed: {type(e).__name__}",
        ) from e
    
    # 将数据流 response 处理成为合法的字符串
    def generate() -> Iterator[str]:
        try:
            for line in response.iter_lines():
                if not line:
                    continue

                if not line.startswith("data: "):
                    continue

                raw_data = line.removeprefix("data: ").strip()

                if raw_data == "[DONE]":
                    break

                data = json.loads(raw_data)

                choices = data.get("choices", [])

                if not choices:
                    continue

                delta = choices[0].get("delta", {})
                content = delta.get("content")

                if content:
                    yield content

        except (
            httpx.RequestError,
            json.JSONDecodeError,
            KeyError,
            IndexError,
        ) as e:
            raise LLMStreamError(
                f"stream interrupted: {type(e).__name__}"
            ) from e

        finally:
            response.close()
            client.close()

    return generate()