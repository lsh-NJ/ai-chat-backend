# httpx

> `httpx` 是 Python 里的 HTTP 请求库
>
> 用户浏览器 -> 请求你的 FastAPI 后端  
> 你的 FastAPI 后端 -> 用 httpx 请求外部 API  
> 外部 API -> 返回数据给你的后端  
> 你的后端 -> 再返回给用户

1. 创建一个`app/services/external_api.py`文件：

   添加`headers`

   ```python
   import httpx


   def fetch_github_status() -> dict:
       url = "https://api.github.com"

   	headers = {
       	"Accept": "application/vnd.github+json",
       	"User-Agent": "ai-chat-backend/0.1", # 标明来源
   	}

       response = httpx.get(url, headers = headers, timeout=10.0)
       response.raise_for_status() # 检查本次 HTTP 响应状态码是否异常

       return response.json()
   ```
2. 在`main.py`中添加测试接口：

   记得 import

   ```python
   @app.get("/external/test")
   def external_test():
       data = fetch_github_status()

       return {
           "message": "External API request success",
           "current_user_url": data.get("current_user_url"),
           "repository_url": data.get("repository_url"),
       }
   ```
3. 处理访问异常：

   修改`external_api.py`:

   ```python
   import httpx
   from fastapi import HTTPException


   def fetch_github_status() -> dict:
       url = "https://api.github.com"

       headers = {
           "Accept": "application/vnd.github+json",
           "User-Agent": "ai-chat-backend/0.1",
       }

       try:
           response = httpx.get(
               url,
               headers=headers,
               timeout=10.0,
           )
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
   ```
4. 代理访问：

   创建一个 httpx 客户端，请求外部 API 时走 `.env` 里配置的代理。

   ```python
   with httpx.Client(
       proxy=settings.proxy_url,
       headers=headers,
       timeout=10.0,
   ) as client:
       response = client.get(url)
   ```

‍
