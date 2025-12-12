#!/bin/bash
# Manual script to upload all scripts to S3 for initial setup

set -e

BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$BRANCH" = "release" ]; then
    ENV="production"
elif [ "$BRANCH" = "staging" ]; then
    ENV="staging"
else
    ENV="staging"
fi

BUCKET="lacrei-saude-${ENV}-scripts"

echo "Current branch: $BRANCH"
echo "Environment: $ENV"
echo "Uploading scripts to s3://${BUCKET}..."
echo ""

for script in terraform/modules/lacrei-infra/scripts/*.sh; do
    FILENAME=$(basename "$script")
    echo "Uploading $FILENAME..."
    aws s3 cp "$script" "s3://${BUCKET}/${FILENAME}"
done

echo ""
echo "✓ All scripts uploaded successfully!"
