# Cool Stuff

## In Use

**Backend**
- FastAPI
- PostgreSQL
- PostGIS
- pgvector
- TiTiler
- rasterio
- ARQ
- Redis
- MinIO

**ML / Inference**
- Triton Inference Server
- SAM (Segment Anything Model)
- CLIP

**Frontend**
- MapLibre GL JS
- deck.gl
- Plotly

---

## Considered, Not Used

| Tool | What it does | Why skipped |
|---|---|---|
| Qdrant | Vector database | replaced by pgvector |
| Kepler.gl | Geo analytics UI | too opinionated, conflicts with dumb-frontend approach |
| Celery | Job queue | ARQ chosen instead (async-native, Redis-backed) |
| Mapbox GL JS | Map library | MapLibre is the open-source fork with the same API |
| Leaflet | Map library | less suited for high-performance data layers |
| H3 | Hexagonal geo grid (Uber) | worth revisiting for geographic clustering/aggregation |
| GeoPandas | Geo dataframes in Python | useful for data processing pipelines |
| GeoServer | Tile/feature server | TiTiler is lighter and FastAPI-native |


## Sentinal Access: 

● Sentinel-2 on AWS is managed by Element 84 as public COGs. No AWS account needed to read the data.

  The access pattern:

  You search via a STAC API (SpatioTemporal Asset Catalog — the standard index for satellite data), get back S3 URLs, and pass those directly to TiTiler or rasterio.

  STAC endpoint:
  https://earth-search.aws.element84.com/v1

  Python — search and get a file URL:
  from pystac_client import Client

  client = Client.open("https://earth-search.aws.element84.com/v1")

  search = client.search(
      collections=["sentinel-2-l2a"],   # Level-2A = surface reflectance
      bbox=[lon_min, lat_min, lon_max, lat_max],
      datetime="2024-01-01/2024-12-31",
      query={"eo:cloud_cover": {"lt": 20}}
  )

  for item in search.items():
      # item.assets contains band URLs, e.g. visual (RGB), B04, B08, etc.
      print(item.assets["visual"].href)  # → s3://sentinel-cogs/...

  That S3 URL is a COG that TiTiler can read directly — no download needed.

  Install:
  pip install pystac-client

  Key things to know:
  - sentinel-2-l2a is the collection you want (atmospherically corrected)
  - The visual asset is an RGB COG ready for display
  - Individual bands (B04, B08, etc.) are separate assets — useful for NDVI, custom composites
  - Files stay on S3, you stream what you need via TiTiler

  This search logic fits naturally into geo_lib as your imagery discovery module.

