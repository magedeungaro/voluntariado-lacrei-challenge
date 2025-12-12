#!/bin/bash
set -e

# Find the currently running container
RUNNING_CONTAINER=$(docker ps --format '{{.Names}}' | grep -E 'lacrei-(blue|green)' | head -1)

if [ -z "$RUNNING_CONTAINER" ]; then
    echo "Error: No running lacrei container found"
    exit 1
fi

echo "Running migrations using container: $RUNNING_CONTAINER"

# Run migrations in the active container
docker exec "$RUNNING_CONTAINER" python manage.py migrate --noinput

echo "Migrations completed!"
