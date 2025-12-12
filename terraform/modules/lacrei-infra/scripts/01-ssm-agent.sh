#!/bin/bash
set -e

# Ensure SSM agent is installed and running (required for AL2023)
echo "Installing SSM agent..."
dnf install -y amazon-ssm-agent
echo "Enabling SSM agent..."
systemctl enable amazon-ssm-agent
echo "Starting SSM agent..."
systemctl start amazon-ssm-agent
echo "Waiting for SSM agent to start..."
sleep 10
echo "SSM agent status:"
systemctl status amazon-ssm-agent --no-pager || true
echo "SSM agent installation complete"

# Test network connectivity to SSM endpoints
echo "Testing connectivity to SSM endpoints..."
echo "Testing ssm endpoint..."
curl -v https://ssm.${aws_region}.amazonaws.com/ 2>&1 | head -20 || echo "Cannot reach ssm endpoint"
echo "Testing ssmmessages endpoint..."
curl -v https://ssmmessages.${aws_region}.amazonaws.com/ 2>&1 | head -20 || echo "Cannot reach ssmmessages endpoint"
echo "Testing ec2messages endpoint..."
curl -v https://ec2messages.${aws_region}.amazonaws.com/ 2>&1 | head -20 || echo "Cannot reach ec2messages endpoint"
echo "Connectivity test complete"

# Check instance metadata
echo "Testing IMDS connectivity..."
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)
echo "Instance ID: $INSTANCE_ID"
echo "IMDS test complete"
