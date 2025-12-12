#!/bin/bash
set -e

S3_CERT_BUCKET="${certificates_s3_bucket}"
CERT_BACKUP_KEY="letsencrypt-${domain_name}.tar.gz"

# Certificate backup function
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

# Certificate restore function
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
    # backup-certificates.sh is already installed by 05-install-tools.sh
    # Just add to crontab (run daily at 3 AM)
    (crontab -l 2>/dev/null; echo "0 3 * * * /usr/local/bin/backup-certificates.sh") | crontab -
    echo "Certificate backup cron job configured"
}

# Check if manual certificates exist in S3
echo "Checking for manual SSL certificates in S3..."
MANUAL_CERT_EXISTS=false
if aws s3 ls "s3://$S3_CERT_BUCKET/${domain_name}.crt" 2>/dev/null && \
   aws s3 ls "s3://$S3_CERT_BUCKET/${domain_name}.key" 2>/dev/null; then
    echo "Found manual certificates in S3, downloading..."
    aws s3 cp "s3://$S3_CERT_BUCKET/${domain_name}.crt" "/etc/ssl/${domain_name}.crt"
    aws s3 cp "s3://$S3_CERT_BUCKET/${domain_name}.key" "/etc/ssl/${domain_name}.key"
    aws s3 cp "s3://$S3_CERT_BUCKET/${domain_name}.ca-bundle" "/etc/ssl/${domain_name}.ca-bundle" 2>/dev/null || true
    chmod 644 "/etc/ssl/${domain_name}.crt"
    chmod 600 "/etc/ssl/${domain_name}.key"
    [ -f "/etc/ssl/${domain_name}.ca-bundle" ] && chmod 644 "/etc/ssl/${domain_name}.ca-bundle"
    echo "✓ Manual certificates downloaded and secured"
    MANUAL_CERT_EXISTS=true
fi

# Get SSL certificate with Let's Encrypt if no manual cert
echo "Managing SSL certificates..."
if [ ! -z "${domain_name}" ] && [ "${domain_name}" != "_" ]; then
    
    # If no manual cert, try Let's Encrypt
    if [ "$MANUAL_CERT_EXISTS" = false ]; then
        # Try to restore existing Let's Encrypt certificates first
        if restore_certificates; then
            echo "Using restored Let's Encrypt certificates"
        else
            echo "Obtaining new SSL certificate from Let's Encrypt..."
            
            # Start nginx first (certbot needs it running)
            echo "Starting nginx for Let's Encrypt verification..."
            systemctl start nginx || echo "Warning: nginx start had issues, continuing anyway"
            sleep 2
            
            # Use production Let's Encrypt for all environments
            CERTBOT_FLAGS="--nginx -d ${domain_name} --non-interactive --agree-tos --email ${ssl_email} --redirect --no-eff-email"
            
            # Obtain certificate
            if certbot $CERTBOT_FLAGS; then
                echo "✓ SSL certificate obtained successfully"
                # Backup the new certificate
                backup_certificates
            else
                echo "Failed to obtain SSL certificate. Check DNS configuration or rate limits."
            fi
        fi
        
        # Create symlinks to Let's Encrypt certificates for nginx
        echo "Creating symlinks to Let's Encrypt certificates..."
        if [ -d "/etc/letsencrypt/live/${domain_name}" ]; then
            ln -sf "/etc/letsencrypt/live/${domain_name}/fullchain.pem" "/etc/ssl/${domain_name}.crt"
            ln -sf "/etc/letsencrypt/live/${domain_name}/privkey.pem" "/etc/ssl/${domain_name}.key"
            ln -sf "/etc/letsencrypt/live/${domain_name}/chain.pem" "/etc/ssl/${domain_name}.ca-bundle"
            echo "✓ Symlinks created"
        else
            echo "Warning: Let's Encrypt certificate directory not found"
        fi
        
        # Setup automatic backup cron job for Let's Encrypt
        setup_cert_backup_cron
    fi
    
    echo "SSL certificate setup completed for ${environment}"
else
    echo "No domain name configured, skipping SSL setup"
fi

# Final nginx startup/reload with certificates
echo "Starting/reloading nginx with SSL certificates..."
if nginx -t; then
    systemctl restart nginx
    echo "✓ Nginx running with SSL"
else
    echo "ERROR: Nginx configuration test failed"
    nginx -t 2>&1 || true
    exit 1
fi
