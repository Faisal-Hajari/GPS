# Monorepo Structure Summary

## 1. Directory Layout
├── apps/
│   └── web-client/            # Vue.js frontend (pnpm/npm)
├── services/                  # Backend Microservices (Polyglot)
│   ├── stac-api/              # Python + uv (STAC/COG serving)
│   ├── gis-engine/            # Python + uv (PostGIS logic)
│   └── ai-serving/            # Triton Server + Python wrappers
├── packages/                  # Reusable Internal Libraries
│   ├── shared-py/             # Common GIS/AI logic (Geometry utils, etc.)
│   ├── database/              # PostGIS migrations & SQL schemas
│   └── ui-lib/                # Shared Vue components
├── infrastructure/            # DevOps & IaC
│   ├── docker/                # Shared base images (e.g., GDAL/Python base)
│   ├── terraform/             # Cloud resources (S3, RDS, EKS)
│   └── helm/                  # K8s Orchestration
│       └── gps-app/           # Umbrella Chart (links all services)
├── pyproject.toml             # uv Workspace Root (links services & packages)
├── uv.lock                    # Unified Python lockfile
└── docker-compose.yml         # Local development orchestration

## 2. Key Technology Integrations

### Python Management (uv)
- **Workspaces:** The root `pyproject.toml` uses `[tool.uv.workspace]` to manage all services.
- **Local Linking:** Services reference `shared-py` via relative paths: 
  `shared-utils = { path = "../../packages/shared-py", editable = true }`.
- **Consistency:** One `uv.lock` ensures all services (GIS, AI, STAC) use the same library versions (e.g., identical `gdal` or `shapely` versions).

### Containerization (Docker)
- **Multi-stage Builds:** Dockerfiles use `COPY --from` to pull code from `packages/` without bloating the final production image.
- **Shared Bases:** Heavy GIS dependencies are defined in `infrastructure/docker/` to speed up build times for individual services.

### Deployment (Helm)
- **Umbrella Chart:** A single chart in `infrastructure/helm/gps-app/` manages the deployment of the Vue frontend, Python APIs, and Triton server as a single unit.
- **Global Values:** S3 bucket names and PostGIS credentials are managed in a central `values.yaml`.

## 3. Workflow Benefits
- **Atomic Commits:** Update a database schema, the Python logic, and the Helm deployment in one Git commit.
- **Shared Logic:** A single change in `packages/shared-py` is instantly available to both the AI serving and GIS services.
- **Scalability:** New services (e.g., a Rust-based tiling engine) can be added as new folders without disrupting existing logic.
