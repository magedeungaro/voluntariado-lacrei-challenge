#!/bin/bash
set -e

# Create nginx config for blue/green deployment
DOMAIN_NAME="${domain_name}"
cat > /etc/nginx/conf.d/lacrei-saude.conf << EOF
upstream lacrei_backend {
    # Blue deployment (default)
    server 127.0.0.1:8001;
}

# HTTP server - redirects to HTTPS
server {
    listen 80;
    server_name $DOMAIN_NAME;
    return 301 https://\$http_host\$request_uri;
}

# HTTPS server
server {
    listen 443 ssl;
    server_name $DOMAIN_NAME;

    # SSL certificate paths (will be populated by certbot or manual cert)
    ssl_certificate     /etc/ssl/$DOMAIN_NAME.crt;
    ssl_certificate_key /etc/ssl/$DOMAIN_NAME.key;
    # ssl_trusted_certificate is optional - only include if file exists
    # ssl_trusted_certificate /etc/ssl/$DOMAIN_NAME.ca-bundle;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://lacrei_backend;
        proxy_set_header Host \$http_host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /api/v1/health/ {
        proxy_pass http://lacrei_backend;
        proxy_set_header Host \$http_host;
    }

    # Static files (if needed)
    location /static/ {
        alias /opt/lacrei-saude/staticfiles/;
    }
}
EOF

# Disable default nginx site
rm -f /etc/nginx/conf.d/default.conf 2>/dev/null || true

# Disable default server block in nginx.conf to prevent conflicts
echo "Disabling default nginx server block..."
sed -i '/^    server {$/,/^    }$/{s/^/# /}' /etc/nginx/nginx.conf

# Don't start nginx yet - wait for SSL certificates in 06-ssl-certificates.sh
echo "Nginx configured (will start after SSL setup)"
