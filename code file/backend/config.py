from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LegalEase"
    app_env: str = "development"

    api_host: str = "127.0.0.1"
    api_port: int = 8000

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"

    demo_mode: bool = True

    cors_origins: str = (
        "http://localhost:8501,"
        "http://127.0.0.1:8501"
    )

    max_document_chars: int = 50000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()