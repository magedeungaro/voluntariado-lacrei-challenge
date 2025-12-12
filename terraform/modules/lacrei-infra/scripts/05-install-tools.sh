#!/bin/bash
set -e

# Download and install operational scripts from S3
S3_BUCKET="${scripts_s3_bucket}"

echo "Installing operational scripts..."

# Download and process operational scripts
for script in deploy.sh switch-backend.sh run-migrations.sh backup-certificates.sh; do
    echo "Installing $script..."
    # Download from S3
    aws s3 cp "s3://$S3_BUCKET/$script" "/tmp/$script"
    
    # Substitute template variables (same as bootstrap does)
    sed -e "s|\${aws_region}|${aws_region}|g" \
        -e "s|\${ecr_repository_url}|${ecr_repository_url}|g" \
        -e "s|\${certificates_s3_bucket}|${certificates_s3_bucket}|g" \
        -e "s|\${domain_name}|${domain_name}|g" \
        "/tmp/$script" > "/usr/local/bin/$script"
    
    chmod +x "/usr/local/bin/$script"
    rm "/tmp/$script"
done

echo "✓ Operational scripts installed"
