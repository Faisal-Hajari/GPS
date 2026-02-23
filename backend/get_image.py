from datetime import datetime, timedelta
import requests
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds
from rasterio.enums import Resampling
from PIL import Image

TOP_LEFT     = [24.756608, 46.565257]
TOP_RIGHT    = [24.786204, 46.686208]
BOTTOM_LEFT  = [24.706316, 46.577833]
BOTTOM_RIGHT = [24.710053, 46.698548]

STAC_URL = "https://eod-catalog-svc-prod.astraea.earth"

COLLECTIONS_BY_RESOLUTION = [
    {"name": "naip",                "gsd": 1,   "visual_asset": "analytic_rgbir_cog", "supports_cloud": False},
    {"name": "sentinel2_l2a",       "gsd": 10,  "visual_asset": "TCI_10m",            "supports_cloud": True},
    {"name": "sentinel2_l1c",       "gsd": 10,  "visual_asset": "TCI",                "supports_cloud": True},
    {"name": "landsat8_c2_l1tp_t1", "gsd": 30,  "visual_asset": "B4",                 "supports_cloud": True},
    {"name": "mcd43a4",             "gsd": 500, "visual_asset": "B01",                "supports_cloud": False},
]

def get_bbox(tl, tr, bl, br):
    all_coord = [tl, tr, bl, br]
    lats = [coord[0] for coord in all_coord]
    lons = [coord[1] for coord in all_coord]
    return [min(lons), min(lats), max(lons), max(lats)]

def format_datetime(date_range):
    start = date_range[0].strftime("%Y-%m-%dT%H:%M:%SZ")
    end   = date_range[1].strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"{start}/{end}"

def search_collection(collection, bbox, date_range, max_items=200):
    body = {
        "collections": [collection["name"]],
        "bbox": bbox,
        "datetime": format_datetime(date_range),
        "limit": max_items,
    }

    if collection["supports_cloud"]:
        body["sortby"] = [{"field": "properties.eo:cloud_cover", "direction": "asc"}]

    try:
        response = requests.post(f"{STAC_URL}/search", json=body)
        response.raise_for_status()
        features = response.json().get("features", [])
        return features
    except Exception as e:
        print(f"  Error searching {collection['name']}: {e}")
        return []

def find_best_item(bbox, date_range):
    for collection in COLLECTIONS_BY_RESOLUTION:
        print(f"Searching {collection['name']} (GSD: {collection['gsd']}m)...")
        items = search_collection(collection, bbox, date_range)

        if not items:
            print(f"  No results found.")
            continue

        # Fallback client-side sort by cloud cover
        if collection["supports_cloud"]:
            items.sort(key=lambda i: i.get("properties", {}).get("eo:cloud_cover", 100))

        best = items[0]
        print(f"  Found {len(items)} items. Best cloud cover: {best.get('properties', {}).get('eo:cloud_cover', 'N/A')}%")
        print(f"  Date: {best.get('properties', {}).get('datetime')}")
        return best, collection

    return None, None


now = datetime.now()
bbox = get_bbox(TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT)
date_range = (now - timedelta(weeks=12), now)

item, collection = find_best_item(bbox, date_range)

if item is None:
    print("No items found across any collection.")
    exit()

print(f"\nBest item: {item['id']}")
print(f"Collection: {collection['name']} ({collection['gsd']}m resolution)")

assets = item.get("assets", {})
visual_asset_key = collection["visual_asset"]
if visual_asset_key not in assets:
    # Fallback to first asset with 'data' role, or just first asset
    visual_asset_key = next(
        (k for k, v in assets.items() if "data" in v.get("roles", [])),
        next(iter(assets))
    )
    print(f"  Fallback asset used: {visual_asset_key}")

visual_href = assets[visual_asset_key]["href"]
print(f"Asset URL: {visual_href}")

with rasterio.open(visual_href) as src:
    bounds_in_crs = transform_bounds("EPSG:4326", src.crs, *bbox)
    window = from_bounds(*bounds_in_crs, transform=src.transform)
    data = src.read(
        [1, 2, 3],
        window=window,
        resampling=Resampling.bilinear
    )

img = Image.fromarray(data.transpose(1, 2, 0))
img.save("image.png")
print("Saved image.png")