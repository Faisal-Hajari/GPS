# Set environment variables for database connection
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=gps
export PGUSER=postgres  # A user with admin privileges
export PGPASSWORD=admin

uv run pypgstac migrate