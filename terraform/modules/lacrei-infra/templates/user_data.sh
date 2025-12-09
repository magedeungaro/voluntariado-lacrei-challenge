#!/bin/bash
set -e

# Update system
dnf update -y

# Install Docker
dnf install -y docker
systemctl enable docker
systemctl start docker

# Install nginx
dnf install -y nginx
systemctl enable nginx

# Install AWS CLI (for ECR login)
dnf install -y aws-cli

# Add ec2-user to docker group
usermod -aG docker ec2-user

# Create app directory
mkdir -p /opt/lacrei-saude
cd /opt/lacrei-saude

# Create environment file
cat > /opt/lacrei-saude/.env << 'EOF'
DEBUG=false
SECRET_KEY=${django_secret_key}
DB_NAME=${db_name}
DB_USER=${db_user}
DB_PASSWORD=${db_password}
DB_HOST=${db_host}
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
ENVIRONMENT=${environment}
EOF

chmod 600 /opt/lacrei-saude/.env

# Create nginx config for blue/green deployment
cat > /etc/nginx/conf.d/lacrei-saude.conf << 'EOF'
upstream lacrei_backend {
    # Blue deployment (default)
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://lacrei_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /api/v1/health/ {
        proxy_pass http://lacrei_backend;
        proxy_set_header Host $host;
    }

    # Static files (if needed)
    location /static/ {
        alias /opt/lacrei-saude/staticfiles/;
    }
}
EOF

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

# Check health
if curl -sf "http://localhost:$PORT/api/v1/health/" > /dev/null; then
    echo "Deployment to $SLOT successful!"
    echo "Run 'sudo /usr/local/bin/switch-backend.sh $SLOT' to switch traffic"
else
    echo "Health check failed!"
    docker logs "$CONTAINER_NAME"
    exit 1
fi
DEPLOYEOF

chmod +x /usr/local/bin/deploy.sh

# Create migration script
cat > /usr/local/bin/run-migrations.sh << 'MIGRATEEOF'
#!/bin/bash
set -e

ECR_REPO="${ecr_repository_url}"
AWS_REGION="${aws_region}"

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO

# Run migrations
docker run --rm \
    --env-file /opt/lacrei-saude/.env \
    "$ECR_REPO:latest" \
    python manage.py migrate --noinput

echo "Migrations completed!"
MIGRATEEOF

chmod +x /usr/local/bin/run-migrations.sh

# Disable default nginx site
rm -f /etc/nginx/conf.d/default.conf 2>/dev/null || true

# Start nginx
systemctl start nginx

# Log completion
echo "EC2 setup completed at $(date) - Environment: ${environment}" >> /var/log/user-data.log
