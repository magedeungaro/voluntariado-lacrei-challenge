#!/bin/bash
set -e

# Create blue/green switch script
cat > /usr/local/bin/switch-backend.sh << 'SWITCHEOF'
#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: $0 blue|green"
    echo "Current backend:"
    grep -E "server 127.0.0.1" /etc/nginx/conf.d/lacrei-saude.conf
    exit 1
fi

TARGET="$1"
CONF="/etc/nginx/conf.d/lacrei-saude.conf"

if [ "$TARGET" = "blue" ]; then
    NEW_SERVER="server 127.0.0.1:8001;"
elif [ "$TARGET" = "green" ]; then
    NEW_SERVER="server 127.0.0.1:8002;"
else
    echo "Unknown target: $TARGET. Use 'blue' or 'green'"
    exit 1
fi

# Backup current config
cp "$CONF" "$CONF.bak.$(date +%s)"

# Update upstream server
sed -i "s/server 127.0.0.1:[0-9]*;/$NEW_SERVER/" "$CONF"

# Test nginx config
nginx -t

# Reload nginx
systemctl reload nginx

echo "Switched backend to $TARGET"
echo "Current config:"
grep -E "server 127.0.0.1" "$CONF"
SWITCHEOF

chmod +x /usr/local/bin/switch-backend.sh

# Create deployment script
cat > /usr/local/bin/deploy.sh << 'DEPLOYEOF'
#!/bin/bash
set -e

SLOT="$1"  # blue or green
IMAGE_TAG="$${2:-latest}"

if [ -z "$SLOT" ]; then
    echo "Usage: $0 <blue|green> [image-tag]"
    exit 1
fi

if [ "$SLOT" = "blue" ]; then
    PORT=8001
elif [ "$SLOT" = "green" ]; then
    PORT=8002
else
    echo "Unknown slot: $SLOT. Use 'blue' or 'green'"
    exit 1
fi

CONTAINER_NAME="lacrei-$SLOT"
ECR_REPO="${ecr_repository_url}"
AWS_REGION="${aws_region}"

echo "Deploying to $SLOT slot (port $PORT)..."

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO

# Pull latest image
docker pull "$ECR_REPO:$IMAGE_TAG"

# Stop old container if exists
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true

# Run new container
docker run -d \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    --env-file /opt/lacrei-saude/.env \
    -p "$PORT:8000" \
    "$ECR_REPO:$IMAGE_TAG"

# Wait for container to be healthy
echo "Waiting for container to be healthy..."
sleep 10

# Coleta arquivos estáticos
echo "Coletando arquivos estáticos..."
docker exec "$CONTAINER_NAME" python manage.py collectstatic --noinput

# Copia arquivos estáticos para o host
echo "Copiando arquivos estáticos para o host..."
mkdir -p /opt/lacrei-saude/staticfiles
docker cp "$CONTAINER_NAME:/app/staticfiles/." /opt/lacrei-saude/staticfiles/
chmod -R 755 /opt/lacrei-saude/staticfiles

# Verifica saúde
if curl -4 -sf "http://localhost:$PORT/api/v1/health/" > /dev/null; then
    echo "Deploy para $SLOT realizado com sucesso!"
    echo "Execute 'sudo /usr/local/bin/switch-backend.sh $SLOT' para alternar o tráfego"
else
    echo "Verificação de saúde falhou!"
    docker logs "$CONTAINER_NAME"
    exit 1
fi
DEPLOYEOF

chmod +x /usr/local/bin/deploy.sh

# Create migration script
cat > /usr/local/bin/run-migrations.sh << 'MIGRATEEOF'
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
MIGRATEEOF

chmod +x /usr/local/bin/run-migrations.sh
