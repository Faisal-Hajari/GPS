export PGUSER=postgres
export PGPASSWORD=admin
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=gps
uv run fastapi dev services/stac-api/pgstac/app.py
