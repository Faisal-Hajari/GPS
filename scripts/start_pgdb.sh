#!/bin/bash
set -e

# Kill and remove existing container if it exists
docker kill local-pgdb 2>/dev/null || true
docker rm -f local-pgdb 2>/dev/null || true

if [ -d "./pgdata" ]; then
    echo "Found existing pgdata directory, removing it..."
    rm -rf ./pgdata
    mkdir ./pgdata
fi

# Build the image
docker build -f infrastructure/docker/Dockerfile.postgres -t local-pgdb .

# Run the container in the background
docker run -d \
    --name local-pgdb \
    -e POSTGRES_PASSWORD=admin \
    -e POSTGRES_DB=gps \
    -p 5432:5432 \
    -v ./pgdata:/var/lib/postgresql/data \
    local-pgdb

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until docker exec local-pgdb pg_isready -U postgres; do
    sleep 1
done

# Run pypgstac migrate
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=gps
export PGUSER=postgres
export PGPASSWORD=admin

uv run pypgstac migrate

echo "Database is ready and migrations complete."