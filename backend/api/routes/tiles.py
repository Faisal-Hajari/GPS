import asyncio
from datetime import datetime
from fastapi import APIRouter, Query
from fastapi.responses import Response
from rio_tiler.io import Reader
from titiler.core.utils import render_image
import morecantile
from services.maps.cog_clients import Sentinel2COG
from services.core.utils import cached, timeit
from services.core.config import settings
import logging 

logger = logging.getLogger("uvicorn")
router = APIRouter()


TILE_TIMEOUT_SECONDS = 60


def _tile_intersects_coverage(x: int, y: int, z: int) -> bool:
    tms = morecantile.tms.get("WebMercatorQuad")
    t = tms.bounds(x, y, z)
    west, south, east, north = settings.vite_coverage
    return not (t.right < west or t.left > east or t.top < south or t.bottom > north)


@router.get("/stac/tiles/{z}/{x}/{y}")
async def stac_tile(
    z: int,
    x: int,
    y: int,
    start: datetime = Query(default=datetime(2024, 1, 1)),
    end: datetime = Query(default=datetime(2024, 12, 31)),
):  
    logger.info(f"received request for: /stac/tiles/{z}/{x}/{y} | stac_tile")
    if not _tile_intersects_coverage(x, y, z):
        return Response(status_code=204)
    try:
        cog = Sentinel2COG()
        img_bytes = await asyncio.wait_for(
            asyncio.to_thread(cog.find_tile, x=x, y=y, z=z, date_range=(start, end)),
            timeout=TILE_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        return Response(status_code=204)
    if not img_bytes:
        return Response(status_code=204)
    return Response(content=img_bytes, media_type="image/png")

@cached()
@timeit()
def _read_cog_tile(url: str, x: int, y: int, z: int) -> bytes:
    with Reader(url) as cog:
        image = cog.tile(x, y, z)
    content, _ = render_image(image)
    return content


COG_URL = "https://earth-search.aws.element84.com/v1/search"


@router.get("/cog/tiles/{z}/{x}/{y}")
async def cog_tile(
    z: int,
    x: int,
    y: int,
):
    logger.info("recived request for: /cog/tiles/{z}/{x}/{y} | cog_tile")

    try:
        img_bytes = await asyncio.wait_for(
            asyncio.to_thread(_read_cog_tile, COG_URL, x, y, z),
            timeout=TILE_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        return Response(status_code=204)
    if not img_bytes:
        return Response(status_code=204)
    return Response(content=img_bytes, media_type="image/png")
