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

# Download manual SSL certificates from S3 if they exist
echo "Checking for manual SSL certificates in S3..."
CERT_FILES="${domain_name}.crt ${domain_name}.key ${domain_name}.ca-bundle"

for cert_file in $CERT_FILES; do
    if aws s3 ls "s3://$S3_CERT_BUCKET/$cert_file" 2>/dev/null; then
        echo "Found $cert_file in S3, downloading..."
        aws s3 cp "s3://$S3_CERT_BUCKET/$cert_file" "/etc/ssl/$cert_file"
        chmod 600 "/etc/ssl/$cert_file"
        echo "Downloaded and secured $cert_file"
    fi
done

# Start nginx now (after config is ready)
echo "Starting nginx..."
systemctl start nginx
echo "Nginx started"

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
