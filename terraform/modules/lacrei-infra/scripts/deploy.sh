#!/bin/bash
set -e

SLOT="$1"  # blue or green
IMAGE_TAG="${2:-latest}"

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
