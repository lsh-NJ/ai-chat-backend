import os 

from dotenv import load_dotenv

load_dotenv()

class Settings:
    app_name: str = os.getenv("APP_NAME", "AI Chat Backend")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    test_api_key: str | None = os.getenv("TEST_API_KEY")
    proxy_url: str | None = os.getenv("PROXY_URL")

    deepseek_api_key: str | None = os.getenv("DEEPSEEK_API_KEY")
    deepseek_base_url: str = os.getenv(
        "DEEPSEEK_BASE_URL",
        "https://api.deepseek.com",
    )
    deepseek_model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
    database_path: str = os.getenv("DATABASE_PATH", "data/app.db")


settings = Settings()