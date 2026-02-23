from pystac_client import Client
from datetime import datetime


class COG:
    def get_tile(
        self,
        top_left: tuple[float, float],
        bottom_right: tuple[float, float],
        date_range: tuple[datetime, datetime],
    ) -> str:
        raise NotImplementedError("Subclasses must implement this method")


class Sentinel2COG(COG):
    def __init__(
        self,
        stac_url: str = "https://earth-search.aws.element84.com/v1",
        collection: str = "sentinel-2-c1-l2a",
        max_items: int = 200,
        cloud_cover_key: str = "eo:cloud_cover",
        image_key: str = "visual",
        source_crs: str = "EPSG:4326",
    ):
        self.stac_url = stac_url
        self.collection = collection
        self.max_items = max_items
        self.cloud_cover_key = cloud_cover_key
        self.image_key = image_key
        self.source_crs = source_crs

    def get_tile(
        self,
        # in [lat, lon] order
        top_left: tuple[float, float],
        bottom_right: tuple[float, float],
        date_range: tuple[datetime, datetime],
    ) -> str:
        client = Client.open(self.stac_url)
        search = client.search(
            collections=[self.collection],
            bbox=[top_left[1], bottom_right[0], bottom_right[1], top_left[0]],
            datetime=date_range,
            max_items=self.max_items,
        )
        items = list(search.items())
        max_value_for_cloud_cover = 100 
        items.sort(key=lambda i: i.properties.get(self.cloud_cover_key, max_value_for_cloud_cover))
        item = items[0]
        return item.assets[self.image_key].href
        
