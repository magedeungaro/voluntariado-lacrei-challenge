#!/bin/bash
set -e

# Update system
echo "Updating system packages..."
dnf update -y

# Install Docker
echo "Installing Docker..."
dnf install -y docker
systemctl enable docker
systemctl start docker
echo "Docker installed and started"

# Install nginx
echo "Installing nginx..."
dnf install -y nginx
systemctl enable nginx
echo "Nginx installed"

# Install Certbot for SSL certificates
echo "Installing Certbot..."
dnf install -y python3 augeas-libs
python3 -m venv /opt/certbot
/opt/certbot/bin/pip install --upgrade pip
/opt/certbot/bin/pip install certbot certbot-nginx
ln -sf /opt/certbot/bin/certbot /usr/bin/certbot
echo "Certbot installed"

# Install AWS CLI (for ECR login)
echo "Installing AWS CLI..."
dnf install -y aws-cli
echo "AWS CLI installed"

# Install cron
echo "Installing cronie..."
dnf install -y cronie
systemctl enable crond
systemctl start crond
echo "Cron installed and started"

# Add ec2-user to docker group
usermod -aG docker ec2-user
