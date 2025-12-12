#!/bin/bash
set -e

# Final SSM agent check
echo "Final SSM agent status check..."
systemctl status amazon-ssm-agent --no-pager || true
echo "SSM agent logs:"
journalctl -u amazon-ssm-agent --no-pager -n 50 || true

echo "=========================================="
echo "EC2 setup completed successfully!"
echo "Environment: ${environment}"
echo "Timestamp: $(date)"
echo "=========================================="
