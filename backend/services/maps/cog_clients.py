from datetime import datetime

from pystac_client import Client
import morecantile
from rio_tiler.io import COGReader
from rio_tiler.mosaic import mosaic_reader
from rio_tiler.mosaic.methods.defaults import FirstMethod
from rasterio.errors import RasterioIOError
from rio_tiler.errors import TileOutsideBounds

from services.core.utils import cached, timeit


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
    ):
        self.stac_url = stac_url
        self.collection = collection
        self.max_items = max_items
        self.cloud_cover_key = cloud_cover_key
        self.max_cloud_cover = max_cloud_cover
        self.image_key = image_key
        self.source_crs = source_crs
            
    
    @timeit()
    @cached(maxsize=1024)
    def find_tile(
        self, x: int, y: int, z: int, date_range: tuple[datetime, datetime]
    ) -> bytes:
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

def read_tile(url: str, x: int, y: int, z: int, **kw):
    with COGReader(url) as cog:
        return cog.tile(x, y, z, **kw)
