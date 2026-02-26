import os
os.environ.update({
    "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": "YES",   # fewer round trips
    "GDAL_HTTP_MULTIPLEX": "YES",                  # HTTP/2 pipelining
    "CPL_VSIL_CURL_CACHE_SIZE": "200000000",       # 200MB VSIL curl cache
    "GDAL_CACHEMAX": "512",                        # 512MB GDAL block cache
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",   # skip directory listing
    "GDAL_HTTP_MAX_RETRY": "3",
    "GDAL_HTTP_RETRY_DELAY": "1",
})

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.tiles import router as tiles_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(tiles_router)