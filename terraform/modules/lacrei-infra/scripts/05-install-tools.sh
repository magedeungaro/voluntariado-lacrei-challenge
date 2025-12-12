#!/bin/bash
set -e

# Variables are passed from bootstrap via environment or command line args
# These will be substituted by bootstrap.sh before execution
S3_BUCKET="${scripts_s3_bucket}"
AWS_REGION="${aws_region}"
ECR_REPO="${ecr_repository_url}"
CERTS_BUCKET="${certificates_s3_bucket}"
DOMAIN="${domain_name}"

echo "Installing operational scripts..."
echo "Using: AWS_REGION=$AWS_REGION, ECR_REPO=$ECR_REPO"

# Create environment file that scripts can source
cat > /etc/lacrei-env.sh << EOF
export AWS_REGION="$AWS_REGION"
export ECR_REPO="$ECR_REPO"
export CERTIFICATES_S3_BUCKET="$CERTS_BUCKET"
export DOMAIN_NAME="$DOMAIN"
EOF

chmod 644 /etc/lacrei-env.sh

# Download operational scripts and make them source the environment
for script in deploy.sh switch-backend.sh run-migrations.sh backup-certificates.sh; do
    echo "Installing $script..."
    aws s3 cp "s3://$S3_BUCKET/$script" "/usr/local/bin/$script"
    chmod +x "/usr/local/bin/$script"
done

echo "✓ Operational scripts installed with environment at /etc/lacrei-env.sh"
