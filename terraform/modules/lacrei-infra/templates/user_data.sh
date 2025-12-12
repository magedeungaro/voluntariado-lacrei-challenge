#!/bin/bash
set -e

# Setup logging - redirect all output to log file and console
exec > >(tee /var/log/user-data.log) 2>&1

echo "=========================================="
echo "Starting user-data script execution"
echo "Environment: ${environment}"
echo "Timestamp: $(date)"
echo "=========================================="

# Ensure SSM agent is installed and running (required for AL2023)
echo "Installing SSM agent..."
dnf install -y amazon-ssm-agent
echo "Enabling SSM agent..."
systemctl enable amazon-ssm-agent
echo "Starting SSM agent..."
systemctl start amazon-ssm-agent
echo "Waiting for SSM agent to start..."
sleep 10
echo "SSM agent status:"
systemctl status amazon-ssm-agent --no-pager || true
echo "SSM agent installation complete"

# Test network connectivity to SSM endpoints
echo "Testing connectivity to SSM endpoints..."
echo "Testing ssm endpoint..."
curl -v https://ssm.${aws_region}.amazonaws.com/ 2>&1 | head -20 || echo "Cannot reach ssm endpoint"
echo "Testing ssmmessages endpoint..."
curl -v https://ssmmessages.${aws_region}.amazonaws.com/ 2>&1 | head -20 || echo "Cannot reach ssmmessages endpoint"
echo "Testing ec2messages endpoint..."
curl -v https://ec2messages.${aws_region}.amazonaws.com/ 2>&1 | head -20 || echo "Cannot reach ec2messages endpoint"
echo "Connectivity test complete"

# Check instance metadata
echo "Testing IMDS connectivity..."
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)
echo "Instance ID: $INSTANCE_ID"
echo "IMDS test complete"

# Update system
echo "Updating system packages..."
dnf update -y

# Install Docker
echo "Installing Docker..."
dnf install -y docker
systemctl enable docker
systemctl start docker
echo "Docker installed and started"

# Install nginx
echo "Installing nginx..."
dnf install -y nginx
systemctl enable nginx
echo "Nginx installed"

# Install Certbot for SSL certificates
echo "Installing Certbot..."
dnf install -y python3 augeas-libs
python3 -m venv /opt/certbot
/opt/certbot/bin/pip install --upgrade pip
/opt/certbot/bin/pip install certbot certbot-nginx
ln -sf /opt/certbot/bin/certbot /usr/bin/certbot
echo "Certbot installed"

# Install AWS CLI (for ECR login)
echo "Installing AWS CLI..."
dnf install -y aws-cli
echo "AWS CLI installed"

# Add ec2-user to docker group
usermod -aG docker ec2-user

# Create app directory
echo "Creating app directory..."
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
ALLOWED_HOSTS=localhost,127.0.0.1,${domain_name}
CORS_ALLOWED_ORIGINS=https://${domain_name}
CSRF_TRUSTED_ORIGINS=https://${domain_name}
USE_HTTPS=true
ENVIRONMENT=${environment}
EOF

chmod 600 /opt/lacrei-saude/.env

# Create nginx config for blue/green deployment
cat > /etc/nginx/conf.d/lacrei-saude.conf << 'EOF'
upstream lacrei_backend {
    # Blue deployment (default)
    server 127.0.0.1:8001;
}

# HTTP server - redirects to HTTPS
server {
    listen 80;
    server_name ${domain_name};
    return 301 https://\$host\$request_uri;
}

# HTTPS server
server {
    listen 443 ssl;
    server_name ${domain_name};

    # SSL certificate paths (will be populated by certbot or manual cert)
    ssl_certificate     /etc/ssl/${domain_name}.crt;
    ssl_certificate_key /etc/ssl/${domain_name}.key;
    ssl_trusted_certificate /etc/ssl/${domain_name}.ca-bundle;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://lacrei_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /api/v1/health/ {
        proxy_pass http://lacrei_backend;
        proxy_set_header Host \$host;
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

# Disable default nginx site
rm -f /etc/nginx/conf.d/default.conf 2>/dev/null || true

# Disable default server block in nginx.conf to prevent conflicts
echo "Disabling default nginx server block..."
sed -i '/^    server {$/,/^    }$/{s/^/# /}' /etc/nginx/nginx.conf

# Download manual SSL certificates from S3 if they exist
echo "Checking for manual SSL certificates in S3..."
S3_CERT_BUCKET="${certificates_s3_bucket}"
CERT_FILES="${domain_name}.crt ${domain_name}.key ${domain_name}.ca-bundle"

for cert_file in $CERT_FILES; do
    if aws s3 ls "s3://$S3_CERT_BUCKET/$cert_file" 2>/dev/null; then
        echo "Found $cert_file in S3, downloading..."
        aws s3 cp "s3://$S3_CERT_BUCKET/$cert_file" "/etc/ssl/$cert_file"
        chmod 600 "/etc/ssl/$cert_file"
        echo "Downloaded and secured $cert_file"
    else
        echo "Manual certificate $cert_file not found in S3, will use Let's Encrypt"
    fi
done

# Test nginx configuration
echo "Testing nginx configuration..."
nginx -t

# Start nginx
echo "Starting nginx..."
systemctl start nginx
echo "Nginx started"

# Certificate backup/restore functions
S3_CERT_BUCKET="${certificates_s3_bucket}"
CERT_BACKUP_KEY="letsencrypt-${domain_name}.tar.gz"

backup_certificates() {
    echo "Backing up certificates to S3..."
    if [ -d "/etc/letsencrypt" ]; then
        tar -czf /tmp/letsencrypt-backup.tar.gz -C /etc letsencrypt
        aws s3 cp /tmp/letsencrypt-backup.tar.gz "s3://$S3_CERT_BUCKET/$CERT_BACKUP_KEY"
        rm -f /tmp/letsencrypt-backup.tar.gz
        echo "Certificate backup completed"
    else
        echo "No certificates to backup"
    fi
}

restore_certificates() {
    echo "Attempting to restore certificates from S3..."
    if aws s3 ls "s3://$S3_CERT_BUCKET/$CERT_BACKUP_KEY" 2>/dev/null; then
        echo "Found existing certificates in S3, restoring..."
        aws s3 cp "s3://$S3_CERT_BUCKET/$CERT_BACKUP_KEY" /tmp/letsencrypt-backup.tar.gz
        tar -xzf /tmp/letsencrypt-backup.tar.gz -C /etc/
        rm -f /tmp/letsencrypt-backup.tar.gz
        echo "Certificates restored from S3"
        return 0
    else
        echo "No existing certificates found in S3"
        return 1
    fi
}

# Setup cron job for certificate backup (daily)
setup_cert_backup_cron() {
    echo "Setting up certificate backup cron job..."
    cat > /usr/local/bin/backup-certificates.sh << 'BACKUPEOF'
#!/bin/bash
S3_CERT_BUCKET="${certificates_s3_bucket}"
CERT_BACKUP_KEY="letsencrypt-${domain_name}.tar.gz"

if [ -d "/etc/letsencrypt" ]; then
    tar -czf /tmp/letsencrypt-backup.tar.gz -C /etc letsencrypt
    aws s3 cp /tmp/letsencrypt-backup.tar.gz "s3://$S3_CERT_BUCKET/$CERT_BACKUP_KEY"
    rm -f /tmp/letsencrypt-backup.tar.gz
    logger "SSL certificates backed up to S3"
fi
BACKUPEOF
    chmod +x /usr/local/bin/backup-certificates.sh
    
    # Add to crontab (run daily at 3 AM)
    (crontab -l 2>/dev/null; echo "0 3 * * * /usr/local/bin/backup-certificates.sh") | crontab -
    echo "Certificate backup cron job configured"
}

# Get SSL certificate with Certbot or manual cert from S3
echo "Managing SSL certificates..."
if [ ! -z "${domain_name}" ] && [ "${domain_name}" != "_" ]; then
    # Wait for nginx to be ready
    sleep 5
    
    # Check if manual certificates exist in S3
    MANUAL_CERT_EXISTS=false
    if aws s3 ls "s3://$S3_CERT_BUCKET/${domain_name}.crt" 2>/dev/null; then
        echo "Found manual certificate in S3, downloading..."
        aws s3 cp "s3://$S3_CERT_BUCKET/${domain_name}.crt" "/etc/ssl/${domain_name}.crt"
        aws s3 cp "s3://$S3_CERT_BUCKET/${domain_name}.key" "/etc/ssl/${domain_name}.key"
        aws s3 cp "s3://$S3_CERT_BUCKET/${domain_name}.ca-bundle" "/etc/ssl/${domain_name}.ca-bundle" 2>/dev/null || true
        chmod 600 "/etc/ssl/${domain_name}.key"
        echo "Manual certificates downloaded from S3"
        MANUAL_CERT_EXISTS=true
        
        # Test and reload nginx with manual cert
        if nginx -t; then
            systemctl reload nginx
            echo "Nginx reloaded with manual certificate"
        else
            echo "Warning: nginx config test failed with manual certificate"
        fi
    fi
    
    # If no manual cert, try Let's Encrypt
    if [ "$MANUAL_CERT_EXISTS" = false ]; then
        # Try to restore existing Let's Encrypt certificates first
        if restore_certificates; then
            echo "Using restored Let's Encrypt certificates"
            # Reload nginx to use restored certificates
            nginx -t && systemctl reload nginx || echo "Warning: nginx reload failed"
        else
            echo "Obtaining new SSL certificate from Let's Encrypt..."
            
            # Use staging server for non-production environments to avoid rate limits
            CERTBOT_FLAGS="--nginx -d ${domain_name} --non-interactive --agree-tos --email ${ssl_email} --redirect --no-eff-email"
            if [ "${environment}" != "production" ]; then
                echo "Using Let's Encrypt staging server for ${environment} environment"
                CERTBOT_FLAGS="$CERTBOT_FLAGS --staging"
            fi
            
            # Obtain certificate
            if certbot $CERTBOT_FLAGS; then
                echo "SSL certificate obtained successfully"
                # Backup the new certificate
                backup_certificates
            else
                echo "Failed to obtain SSL certificate. Check DNS configuration or rate limits."
            fi
        fi
        
        # Setup automatic backup cron job for Let's Encrypt
        setup_cert_backup_cron
    fi
    
    echo "SSL certificate setup completed for ${environment}"
else
    echo "No domain name configured, skipping SSL setup"
fi

# Final SSM agent check
echo "Final SSM agent status check..."
systemctl status amazon-ssm-agent --no-pager || true
echo "SSM agent logs:"
journalctl -u amazon-ssm-agent --no-pager -n 50 || true

echo "=========================================="
echo "EC2 setup completed successfully!"
echo "Environment: ${environment}"
echo "Timestamp: $(date)"
echo "=========================================="
