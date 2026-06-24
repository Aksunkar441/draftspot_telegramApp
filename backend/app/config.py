from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    database_url: str  # postgresql+asyncpg://user:pass@host:port/db
    webhook_base_url: str
    mini_app_url: str | None = None
    webhook_path: str = "/bot/webhook"
    default_city: str = "Тараз"
    init_data_max_age_seconds: int = 24 * 60 * 60
    serverless: bool = False
    cors_origin_regex: str | None = None

    @property
    def effective_mini_app_url(self) -> str:
        return self.mini_app_url or self.webhook_base_url

    @property
    def cors_origins(self) -> list[str]:
        return [
            self.effective_mini_app_url.rstrip("/"),
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]

    class Config:
        env_file = ".env"


settings = Settings()
