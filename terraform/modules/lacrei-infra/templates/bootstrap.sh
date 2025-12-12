#!/bin/bash
set -e

# Bootstrap script - downloads and executes modular scripts from S3
exec > >(tee /var/log/user-data.log) 2>&1

echo "=========================================="
echo "Bootstrap: Downloading scripts from S3"
echo "Environment: ${environment}"
echo "Timestamp: $(date)"
echo "=========================================="

# Create scripts directory
mkdir -p /tmp/setup-scripts
cd /tmp/setup-scripts

# Download all scripts from S3
S3_BUCKET="${scripts_s3_bucket}"
SCRIPTS=(
  "00-init.sh"
  "01-ssm-agent.sh"
  "02-system-packages.sh"
  "03-app-setup.sh"
  "04-nginx-config.sh"
  "05-install-tools.sh"
  "06-ssl-certificates.sh"
  "99-finalize.sh"
)

echo "Downloading scripts from s3://$S3_BUCKET..."
for script in "$${SCRIPTS[@]}"; do
  echo "Downloading $script..."
  aws s3 cp "s3://$S3_BUCKET/$script" "/tmp/setup-scripts/$script"
  chmod +x "/tmp/setup-scripts/$script"
done

echo "All scripts downloaded successfully"
echo "=========================================="

# Execute scripts in order
for script in "$${SCRIPTS[@]}"; do
  echo "=========================================="
  echo "Executing $script..."
  echo "=========================================="
  
  # Create a temporary script with template variables substituted
  TEMP_SCRIPT="/tmp/setup-scripts/temp-$script"
  cat "/tmp/setup-scripts/$script" | \
    sed "s|\$\${aws_region}|${aws_region}|g" | \
    sed "s|\$\${django_secret_key}|${django_secret_key}|g" | \
    sed "s|\$\${db_name}|${db_name}|g" | \
    sed "s|\$\${db_user}|${db_user}|g" | \
    sed "s|\$\${db_password}|${db_password}|g" | \
    sed "s|\$\${db_host}|${db_host}|g" | \
    sed "s|\$\${domain_name}|${domain_name}|g" | \
    sed "s|\$\${environment}|${environment}|g" | \
    sed "s|\$\${ssl_email}|${ssl_email}|g" | \
    sed "s|\$\${certificates_s3_bucket}|${certificates_s3_bucket}|g" | \
    sed "s|\$\${scripts_s3_bucket}|${scripts_s3_bucket}|g" | \
    sed "s|\$\${ecr_repository_url}|${ecr_repository_url}|g" > "$TEMP_SCRIPT"
  
  chmod +x "$TEMP_SCRIPT"
  
  if bash "$TEMP_SCRIPT"; then
    echo "$script completed successfully"
  else
    echo "ERROR: $script failed with exit code $?"
    exit 1
  fi
  
  rm -f "$TEMP_SCRIPT"
done

echo "=========================================="
echo "Bootstrap completed successfully!"
echo "=========================================="

# Cleanup
rm -rf /tmp/setup-scripts
