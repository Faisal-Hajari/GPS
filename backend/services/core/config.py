from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_ENV,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    stac_url: str = "https://earth-search.aws.element84.com/v1"
    vite_coverage: list[float] = [44.7, 22.7, 48.7, 26.7]

settings = Settings()