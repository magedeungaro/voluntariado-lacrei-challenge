#!/bin/bash
set -e

# Create app directory
echo "Creating app directory..."
mkdir -p /opt/lacrei-saude
cd /opt/lacrei-saude

# Create environment file  
cat > /opt/lacrei-saude/.env << EOF
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
