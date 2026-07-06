import os 

from dotenv import load_dotenv

load_dotenv()

class Settings:
    app_name: str = os.getenv("APP_NAME", "AI Chat Backend")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    test_api_key: str | None = os.getenv("TEST_API_KEY")
    proxy_url: str | None = os.getenv("PROXY_URL")

settings = Settings()