from datetime import datetime
import logging

from pystac_client import Client
import morecantile
from rio_tiler.mosaic import mosaic_reader
from rio_tiler.mosaic.methods.defaults import FirstMethod
from rasterio.errors import RasterioIOError
from rio_tiler.errors import TileOutsideBounds

from python_utils import cached, timeit
from cog.utils import read_tile, tile_intersects_coverage

logger = logging.getLogger("cog")

class COG:
    def find_tile(
        self, x: int, y: int, z: int, date_range: tuple[datetime, datetime]
    ) -> bytes:
        raise NotImplementedError("Subclasses must implement this method")


class Sentinel2COG(COG):
    def __init__(
        self,
        stac_url: str = "https://earth-search.aws.element84.com/v1",
        collection: str = "sentinel-2-c1-l2a",
        max_items: int = 10,
        cloud_cover_key: str = "eo:cloud_cover",
        image_key: str = "visual",
        source_crs: str = "EPSG:4326",
        max_cloud_cover: int = 20,
        coverage: list[float] = [
            44.7,
            22.7,
            48.7,
            26.7,
        ],  # a bounding box to only include covered regions in  west, south, east, north
    ):
        self.stac_url = stac_url
        self.collection = collection
        self.max_items = max_items
        self.cloud_cover_key = cloud_cover_key
        self.max_cloud_cover = max_cloud_cover
        self.image_key = image_key
        self.source_crs = source_crs
        self.coverage = coverage

    @timeit(logger=logger)
    @cached(maxsize=1024, logger=logger)
    def find_tile(
        self, x: int, y: int, z: int, date_range: tuple[datetime, datetime]
    ) -> bytes:
        if not tile_intersects_coverage(x, y, z, self.coverage):
            return b""
        tms = morecantile.tms.get("WebMercatorQuad")
        bounds = tms.bounds(x, y, z)

        client = Client.open(self.stac_url)
        search = client.search(
            collections=self.collection,
            bbox=[bounds.left, bounds.bottom, bounds.right, bounds.top],
            datetime=date_range,
            max_items=self.max_items,
            query={self.cloud_cover_key: {"lt": self.max_cloud_cover}},
            sortby=f"+properties.{self.cloud_cover_key}",
        )
        cog_urls = [item.assets[self.image_key].href for item in search.items()]
        if len(cog_urls) == 0:
            return b""
        return self.build_mosaic(tuple(cog_urls), x, y, z)

    def build_mosaic(self, cog_urls, x, y, z) -> bytes:
        if len(cog_urls) == 0:
            return b""  # return a transparent tile a nothing

        img, _ = mosaic_reader(
            cog_urls,
            read_tile,
            x,
            y,
            z,
            pixel_selection=FirstMethod(),
            allowed_exceptions=(RasterioIOError, TileOutsideBounds),
        )
        return img.render(img_format="JPEG")
