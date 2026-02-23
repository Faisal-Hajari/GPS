from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # STAC / Sentinel
    stac_url: str = "https://earth-search.aws.element84.com/v1"

settings = Settings()