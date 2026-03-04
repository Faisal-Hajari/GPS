from pydantic_settings import BaseSettings, SettingsConfigDict
import os

os.environ.update(
    {
        "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": "YES",
        "GDAL_HTTP_MULTIPLEX": "YES",
        "CPL_VSIL_CURL_CACHE_SIZE": "200000000",
        "GDAL_CACHEMAX": "512",
        "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
        "GDAL_HTTP_MAX_RETRY": "3",
        "GDAL_HTTP_RETRY_DELAY": "1",
    }
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    stac_url: str = "https://earth-search.aws.element84.com/v1"
    collection: str = "sentinel-2-c1-l2a"
    max_items: int = 10
    cloud_cover_key: str = "eo:cloud_cover"
    image_key: str = "visual"
    source_crs: str = "EPSG:4326"
    max_cloud_cover: int = 20
    # a bounding box to only include covered regions in  west, south, east, north
    coverage: list[float] = [44.7, 22.7, 48.7, 26.7,]


settings = Settings()
