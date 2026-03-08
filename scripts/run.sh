#!/bin/bash
set -e

# Resolve the project root relative to this script's location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

cleanup() {
    echo ""
    echo "Shutting down all services..."
    kill 0  # Kills all processes in this script's process group
    wait
    echo "All services stopped."
}
trap cleanup SIGINT SIGTERM EXIT

# 1. Start the database (blocking — it waits until ready)
echo "==> Starting PostgreSQL..."
bash scripts/start_pgdb.sh

# 2. Start STAC API in background
echo "==> Starting STAC API..."
(
    export PGUSER=postgres PGPASSWORD=admin PGHOST=localhost PGPORT=5432 PGDATABASE=gps
    uv run fastapi dev services/stac-api/pgstac/app.py
) &

# 3. Start Backend API in background
echo "==> Starting Backend API..."
uv run fastapi dev services/backend-api/api/main.py --port 8001 &

# 4. Start Frontend in background
echo "==> Starting Frontend..."
npm run dev --workspace=@gps/web-client &

# Wait for all background jobs
echo ""
echo "All services started. Press Ctrl+C to stop everything."
wait