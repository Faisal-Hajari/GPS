from datetime import datetime, timedelta
from pystac_client import Client
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds
from rasterio.enums import Resampling
import numpy as np
from PIL import Image
import os 

# Google Maps format: [lat, lon]
# Riyadh
TOP_LEFT    = [24.756608, 46.565257]
TOP_RIGHT   = [24.786204, 46.686208]
BOTTOM_LEFT = [24.706316, 46.577833]
BOTTOM_RIGHT= [24.710053, 46.698548]

# SanFransico
# TOP_LEFT = [37.796223, -122.569981]
# BOTTOM_LEFT = [37.707566, -122.560467]
# TOP_RIGHT = [37.797834, -122.372905]
# BOTTOM_RIGHT= [37.673956, -122.344023]

def get_bbox(tl, tr, bl, br): 
    all_coord = [tl, tr, bl, br]
    lats = [coord[0] for coord in all_coord]
    lons = [coord[1] for coord in all_coord]
    return [min(lons), min(lats), max(lons), max(lats)]
 
now = datetime.now()

bbox:list[float] = get_bbox(TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT)


date_range: tuple[datetime, datetime] = (now - timedelta(weeks=12), now)
stac_url:str = "https://earth-search.aws.element84.com/v1"
collection_name:str = 'sentinel-2-c1-l2a'
max_items:int = 200 

client = Client.open(stac_url)

search = client.search(
    collections=[collection_name],
    bbox=bbox,
    datetime=date_range,
    max_items=max_items
)
items = list(search.items())
print("numb of items: ", len(items))

items = list(search.items())
items.sort(key=lambda i: i.properties.get("eo:cloud_cover", 100))
for item in items:
    print(item.properties.get("eo:cloud_cover", 100))
item = items[0]
visual_href = item.assets["visual"].href  # COG URL

with rasterio.open(visual_href) as src:
    bounds_in_crs = transform_bounds("EPSG:4326", src.crs, *bbox)
    window = from_bounds(*bounds_in_crs, transform=src.transform) 
    data = src.read(
        [1, 2, 3],
        window=window,
        resampling=Resampling.bilinear
    )
# with rasterio.open(item.assets["visual"].href) as src:
#     print("Resolution (m):", src.res)        # e.g. (10.0, 10.0)
    
img = Image.fromarray(data.transpose(1, 2, 0))
img.save("image.png")
print("Saved image.png")

