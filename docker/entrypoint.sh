#!/bin/sh
set -e

echo "Waiting for PostgreSQL at ${DB_HOST}..."
until pg_isready -h "${DB_HOST}" -U "${DATABASE_USER}" -d "${POSTGRES_DB}"; do
  sleep 1
done
echo "PostgreSQL is ready."

exec uv run "$@"
