#!/bin/bash
set -e

# Source environment variables
source /etc/lacrei-env.sh

S3_CERT_BUCKET="$CERTIFICATES_S3_BUCKET"
CERT_BACKUP_KEY="letsencrypt-${DOMAIN_NAME}.tar.gz"

if [ -d "/etc/letsencrypt" ]; then
    tar -czf /tmp/letsencrypt-backup.tar.gz -C /etc letsencrypt
    aws s3 cp /tmp/letsencrypt-backup.tar.gz "s3://$S3_CERT_BUCKET/$CERT_BACKUP_KEY"
    rm -f /tmp/letsencrypt-backup.tar.gz
    logger "SSL certificates backed up to S3"
fi
