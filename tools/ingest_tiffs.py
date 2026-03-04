"""
STAC TIFF Ingestion Script — Sentinel-2 Edition
-------------------------------------------------
Loads directly into pgstac via pypgstac (no transactions extension needed).

Supported filename pattern:
    S2A_T38QRM_20240824T072017_L2A.tif

Requirements:
    uv add pypgstac rasterio shapely pyproj

Usage:
    uv run tools/ingest_tiffs.py
"""

import os
import re
import datetime
import rasterio
from rasterio.warp import transform_bounds
from shapely.geometry import box, mapping
from pypgstac.db import PgstacDB
from pypgstac.load import Loader, Methods


# ─────────────────────────────────────────────
# CONFIG — edit these
# ─────────────────────────────────────────────

PG_USER = "postgres"
PG_PWD = "admin"
PG_DB = "gps"
DATABASE_URL  = f"postgresql://{PG_USER}:{PG_PWD}@localhost:5432/{PG_DB}"
TIFF_DIR      = "/home/fhajari/GPS/downloads"
# TIFF_BASE_URL = "http://0.0.0.0:8600/"   # public URL where TIFFs are accessible
TIFF_BASE_URL = "file:///home/fhajari/GPS/downloads"

COLLECTION_ID          = "sentinel-2-c1-l2a"
COLLECTION_TITLE       = "Sentinel-2 L2A"
COLLECTION_DESCRIPTION = "Sentinel-2 L2A GeoTIFF collection"
COLLECTION_LICENSE     = "Local"

# ─────────────────────────────────────────────

S2_PATTERN = re.compile(
    r"(?P<satellite>S2[AB])_"
    r"(?P<mgrs_tile>T[0-9]{2}[A-Z]{3})_"
    r"(?P<datetime>[0-9]{8}T[0-9]{6})_"
    r"(?P<level>L[12][ABC])"
)


def parse_sentinel2_filename(filename: str) -> dict | None:
    match = S2_PATTERN.search(filename)
    if not match:
        return None
    d = match.groupdict()
    dt = datetime.datetime.strptime(d["datetime"], "%Y%m%dT%H%M%S")
    platform_map = {"S2A": "sentinel-2a", "S2B": "sentinel-2b"}
    return {
        "satellite":   d["satellite"],
        "platform":    platform_map.get(d["satellite"], d["satellite"].lower()),
        "mgrs_tile":   d["mgrs_tile"],
        "datetime":    dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "level":       d["level"],
        "mission":     "sentinel-2",
        "instruments": ["msi"],
    }


def get_tiff_metadata(tiff_path: str) -> dict:
    with rasterio.open(tiff_path) as src:
        west, south, east, north = transform_bounds(src.crs, "EPSG:4326", *src.bounds)
        res_x, res_y = src.res

        # Extract cloud cover from TIFF tags (Sentinel-2 stores it as CLOUD_COVERAGE_ASSESSMENT)
        tags = src.tags()
        raw_cloud = (
            tags.get("CLOUD_COVERAGE_ASSESSMENT")
            or tags.get("eo:cloud_cover")
            or tags.get("CLOUD_COVER")
        )
        try:
            cloud_cover = float(raw_cloud) if raw_cloud is not None else None
        except (ValueError, TypeError):
            cloud_cover = None

        return {
            "bbox":        [west, south, east, north],
            "geometry":    mapping(box(west, south, east, north)),
            "crs":         src.crs.to_epsg(),
            "width":       src.width,
            "height":      src.height,
            "bands":       src.count,
            "resolution":  {"x": res_x, "y": res_y},
            "cloud_cover": cloud_cover,
        }


def build_collection() -> dict:
    now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "type":         "Collection",
        "id":           COLLECTION_ID,
        "title":        COLLECTION_TITLE,
        "description":  COLLECTION_DESCRIPTION,
        "stac_version": "1.0.0",
        "license":      COLLECTION_LICENSE,
        "extent": {
            "spatial":  {"bbox": [[-180, -90, 180, 90]]},
            "temporal": {"interval": [[now, None]]},
        },
        "links": [],
    }


def build_item(tiff_path: str) -> dict:
    filename = os.path.basename(tiff_path)
    item_id  = os.path.splitext(filename)[0]

    tiff_meta = get_tiff_metadata(tiff_path)
    s2_meta   = parse_sentinel2_filename(filename)

    if not s2_meta:
        raise ValueError(
            f"'{filename}' does not match Sentinel-2 pattern: "
            "S2A_T38QRM_20240824T072017_L2A.tif"
        )

    print(f"\n  📄 File      : {filename}")
    print(f"  🛰  Satellite : {s2_meta['satellite']}  |  Tile: {s2_meta['mgrs_tile']}  |  Level: {s2_meta['level']}")
    print(f"  📅 Datetime  : {s2_meta['datetime']}")
    print(f"  🗺  BBox      : {[round(c, 4) for c in tiff_meta['bbox']]}")
    print(f"  📐 Size      : {tiff_meta['width']}px × {tiff_meta['height']}px  |  {tiff_meta['bands']} band(s)")
    print(f"  🔢 Resolution: {tiff_meta['resolution']['x']}m × {tiff_meta['resolution']['y']}m  |  EPSG:{tiff_meta['crs']}")
    print(f"  ☁️  Cloud cover: {tiff_meta['cloud_cover']}%")

    return {
        "type":         "Feature",
        "stac_version": "1.0.0",
        "id":           item_id,
        "collection":   COLLECTION_ID,
        "geometry":     tiff_meta["geometry"],
        "bbox":         tiff_meta["bbox"],
        "properties": {
            "datetime":         s2_meta["datetime"],
            "platform":         s2_meta["platform"],
            "mission":          s2_meta["mission"],
            "instruments":      s2_meta["instruments"],
            "mgrs:utm_zone":    s2_meta["mgrs_tile"],
            "processing:level": s2_meta["level"],
            "proj:epsg":        tiff_meta["crs"],
            "proj:shape":       [tiff_meta["height"], tiff_meta["width"]],
            "gsd":              tiff_meta["resolution"]["x"],
            "eo:cloud_cover":   tiff_meta["cloud_cover"],
        },
        "assets": {
            "visual": {
                "href":      f"{TIFF_BASE_URL.rstrip('/')}/{filename}",
                "type":      "image/tiff; application=geotiff",
                "title":     filename,
                "roles":     ["data"],
                "proj:epsg": tiff_meta["crs"],
            }
        },
        "links": [],
    }


def main():
    print(f"\n🚀 Connecting to pgstac at {DATABASE_URL.split('@')[-1]}\n")

    # Find TIFFs
    tiff_files = [
        os.path.join(TIFF_DIR, f)
        for f in os.listdir(TIFF_DIR)
        if f.lower().endswith((".tif", ".tiff"))
    ]

    if not tiff_files:
        print(f"⚠️  No TIFF files found in '{TIFF_DIR}'")
        return

    # Build all items first (fail fast before touching the DB)
    print(f"📂 Found {len(tiff_files)} TIFF(s). Extracting metadata...")
    items = []
    for tiff_path in tiff_files:
        try:
            items.append(build_item(tiff_path))
        except Exception as e:
            print(f"  ❌ Skipping '{tiff_path}': {e}")

    if not items:
        print("\n❌ No valid items to ingest.")
        return

    # Load into pgstac directly
    with PgstacDB(dsn=DATABASE_URL) as db:
        loader = Loader(db=db)

        # 1. Upsert collection
        print(f"\n📦 Loading collection '{COLLECTION_ID}'...")
        loader.load_collections(
            [build_collection()],
            insert_mode=Methods.upsert,
        )
        print(f"  ✅ Collection ready.")

        # 2. Upsert items
        print(f"\n📥 Loading {len(items)} item(s) into pgstac...")
        loader.load_items(
            items,
            insert_mode=Methods.upsert,
        )
        print(f"  ✅ {len(items)} item(s) loaded.")

    print(f"\n✨ Done! Browse at:")
    print(f"   http://127.0.0.1:8000/collections/{COLLECTION_ID}")
    print(f"   http://127.0.0.1:8000/collections/{COLLECTION_ID}/items\n")


if __name__ == "__main__":
    main()