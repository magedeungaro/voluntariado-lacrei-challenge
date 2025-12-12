#!/bin/bash
set -e

# Download and install operational scripts from S3
S3_BUCKET="${scripts_s3_bucket}"
AWS_REGION="${aws_region}"
ECR_REPO="${ecr_repository_url}"
CERTS_BUCKET="${certificates_s3_bucket}"
DOMAIN="${domain_name}"

echo "Installing operational scripts..."

# Download and process operational scripts
for script in deploy.sh switch-backend.sh run-migrations.sh backup-certificates.sh; do
    echo "Installing $script..."
    # Download from S3
    aws s3 cp "s3://$S3_BUCKET/$script" "/tmp/$script"
    
    # Substitute template variables with actual values
    sed -e "s|\${aws_region}|$AWS_REGION|g" \
        -e "s|\${ecr_repository_url}|$ECR_REPO|g" \
        -e "s|\${certificates_s3_bucket}|$CERTS_BUCKET|g" \
        -e "s|\${domain_name}|$DOMAIN|g" \
        "/tmp/$script" > "/usr/local/bin/$script"
    
    chmod +x "/usr/local/bin/$script"
    rm "/tmp/$script"
done

echo "✓ Operational scripts installed"
