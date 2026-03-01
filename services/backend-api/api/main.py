from api.config import settings

import asyncio
from datetime import datetime

from fastapi import FastAPI
from fastapi import Query
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

from cog import Sentinel2COG

app = FastAPI() 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/stac/tiles/{z}/{x}/{y}")
async def get_tile(
    x:int, 
    y:int, 
    z:int, 
    start_date: datetime = Query(default=datetime(2024, 1, 1)),
    end_date: datetime = Query(default=datetime(2024, 12, 31)),
    timeout:int=5
):
    try:
        cog = Sentinel2COG(
            stac_url=settings.stac_url,
            collection=settings.collection,
            max_items=settings.max_items,
            cloud_cover_key=settings.cloud_cover_key,
            max_cloud_cover=settings.max_cloud_cover,
            image_key=settings.image_key,
            source_crs=settings.source_crs,
            coverage=settings.coverage,
        )
        image_byte= await asyncio.wait_for(
            asyncio.to_thread(cog.find_tile, x=x, y=y, z=z, date_range=(start_date, end_date)),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        return Response(status_code=204)
    if not image_byte: 
        return Response(status_code=404)
    return Response(content=image_byte, media_type="image/png")
    