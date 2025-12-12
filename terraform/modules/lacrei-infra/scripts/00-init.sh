#!/bin/bash
set -e

# Setup logging - redirect all output to log file and console
exec > >(tee /var/log/user-data.log) 2>&1

echo "=========================================="
echo "Starting user-data script execution"
echo "Environment: ${environment}"
echo "Timestamp: $(date)"
echo "=========================================="
