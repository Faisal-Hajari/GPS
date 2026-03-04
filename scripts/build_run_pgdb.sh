docker build -f infrastructure/docker/Dockerfile.postgres -t local-pgdb .
docker run -e POSTGRES_PASSWORD=admin -p 5432:5432 -v pgdata:/var/lib/postgresql/data local-pgdb