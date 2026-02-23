# Architecture Decisions

## Repo Structure

Monorepo with two top-level folders:

```
GPS/
├── gps-backend/
│   ├── api/              # FastAPI app
│   ├── docker/           # Docker Compose orchestration (lowercase)
│   └── triton-models/    # Triton model repository
└── gps-frontend/         # Frontend app
```

The nesting of `api/` inside `gps-backend/` is intentional — other backend services (Triton, PostgreSQL) sit alongside it at the same level, orchestrated via Docker Compose.

---

## Backend Services

| Service | Role |
|---|---|
| FastAPI | Single API entry point for all endpoints |
| PostgreSQL + PostGIS | Geo data storage and spatial queries |
| PostgreSQL + pgvector | Vector/embedding storage, replaces Qdrant |
| TiTiler (mounted in FastAPI) | Dynamic tile server for satellite GeoTIFFs |
| Triton Inference Server | ML inference (SAM, CLIP, others) |
| MinIO | Object storage for GeoTIFF files (S3-compatible, self-hosted) |
| Redis + ARQ | Async job queue for long-running ML inference tasks |

A single PostgreSQL instance runs both PostGIS and pgvector extensions, keeping the data layer unified.

TiTiler reads GeoTIFFs directly from MinIO. Images must be in Cloud-Optimized GeoTIFF (COG) format — conversion happens at ingestion time before files are stored.

---

## Data Pipeline

```
Satellite Image (GeoTIFF)
        |
        ├── convert to COG → MinIO (object storage)
        |                        |
        |         ┌──────────────┴──────────────┐
        |         |                             |
        |    ARQ job (async)               TiTiler
        |         |                        → XYZ tiles → frontend map
        |    geo_lib (internal)
        |    ├── Triton (SAM)  → masks → georeferenced → PostGIS geometries
        |    └── Triton (CLIP) → embeddings            → pgvector
        |
        └── API returns job ID immediately, frontend polls for completion
```

`geo_lib` is an internal Python library inside `gps-backend` that handles all georeferencing logic (pixel coordinates → geo coordinates via rasterio affine transform). It is used by the API and ARQ workers — no geo logic lives in the API layer itself.

---

## Frontend

**Libraries:** MapLibre GL JS + deck.gl + Plotly

**Philosophy:** Dumb frontend. All logic lives in FastAPI endpoints. The frontend only renders what the API returns.

| Endpoint | Returns | Frontend action |
|---|---|---|
| `/tiles/{z}/{x}/{y}` | PNG tile | feeds URL to map |
| `/features?bbox=...` | GeoJSON FeatureCollection | renders as deck.gl layer |
| `/search?q=...` | GeoJSON FeatureCollection | renders as deck.gl layer |
| `/stats?bbox=...` | Plotly-compatible JSON | feeds to Plotly |
| `/segment` | GeoJSON FeatureCollection | renders as deck.gl layer |

Kepler.gl was considered and rejected — it has its own internal state and UI logic that conflicts with the dumb-frontend approach, and does not support custom tile layers as a first-class feature.
