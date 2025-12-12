# S3 Bucket for SSL Certificate Storage
resource "aws_s3_bucket" "certificates" {
  bucket = "${var.project_name}-${var.environment}-certificates"

  tags = {
    Name = "${var.project_name}-${var.environment}-certificates"
  }
}

# Enable versioning for certificate backup
resource "aws_s3_bucket_versioning" "certificates" {
  bucket = aws_s3_bucket.certificates.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable encryption at rest
resource "aws_s3_bucket_server_side_encryption_configuration" "certificates" {
  bucket = aws_s3_bucket.certificates.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "certificates" {
  bucket = aws_s3_bucket.certificates.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle policy to retain old versions for 30 days
resource "aws_s3_bucket_lifecycle_configuration" "certificates" {
  bucket = aws_s3_bucket.certificates.id

  rule {
    id     = "delete-old-versions"
    status = "Enabled"

    filter {
      prefix = ""
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

# S3 Bucket for user-data scripts
resource "aws_s3_bucket" "scripts" {
  bucket = "${var.project_name}-${var.environment}-scripts"

  tags = {
    Name = "${var.project_name}-${var.environment}-scripts"
  }
}

# Enable versioning for scripts
resource "aws_s3_bucket_versioning" "scripts" {
  bucket = aws_s3_bucket.scripts.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable encryption for scripts
resource "aws_s3_bucket_server_side_encryption_configuration" "scripts" {
  bucket = aws_s3_bucket.scripts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access for scripts
resource "aws_s3_bucket_public_access_block" "scripts" {
  bucket = aws_s3_bucket.scripts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle policy for scripts
resource "aws_s3_bucket_lifecycle_configuration" "scripts" {
  bucket = aws_s3_bucket.scripts.id

  rule {
    id     = "delete-old-versions"
    status = "Enabled"

    filter {
      prefix = ""
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

# Upload modular scripts to S3
resource "aws_s3_object" "init_script" {
  bucket = aws_s3_bucket.scripts.id
  key    = "00-init.sh"
  source = "${path.module}/scripts/00-init.sh"
  etag   = filemd5("${path.module}/scripts/00-init.sh")

  tags = {
    Name = "init-script"
  }
}

resource "aws_s3_object" "ssm_agent_script" {
  bucket = aws_s3_bucket.scripts.id
  key    = "01-ssm-agent.sh"
  source = "${path.module}/scripts/01-ssm-agent.sh"
  etag   = filemd5("${path.module}/scripts/01-ssm-agent.sh")

  tags = {
    Name = "ssm-agent-script"
  }
}

resource "aws_s3_object" "system_packages_script" {
  bucket = aws_s3_bucket.scripts.id
  key    = "02-system-packages.sh"
  source = "${path.module}/scripts/02-system-packages.sh"
  etag   = filemd5("${path.module}/scripts/02-system-packages.sh")

  tags = {
    Name = "system-packages-script"
  }
}

resource "aws_s3_object" "app_setup_script" {
  bucket = aws_s3_bucket.scripts.id
  key    = "03-app-setup.sh"
  source = "${path.module}/scripts/03-app-setup.sh"
  etag   = filemd5("${path.module}/scripts/03-app-setup.sh")

  tags = {
    Name = "app-setup-script"
  }
}

resource "aws_s3_object" "nginx_config_script" {
  bucket = aws_s3_bucket.scripts.id
  key    = "04-nginx-config.sh"
  source = "${path.module}/scripts/04-nginx-config.sh"
  etag   = filemd5("${path.module}/scripts/04-nginx-config.sh")

  tags = {
    Name = "nginx-config-script"
  }
}

resource "aws_s3_object" "install_tools_script" {
  bucket = aws_s3_bucket.scripts.id
  key    = "05-install-tools.sh"
  source = "${path.module}/scripts/05-install-tools.sh"
  etag   = filemd5("${path.module}/scripts/05-install-tools.sh")

  tags = {
    Name = "install-tools-script"
  }
}

resource "aws_s3_object" "ssl_certificates_script" {
  bucket = aws_s3_bucket.scripts.id
  key    = "06-ssl-certificates.sh"
  source = "${path.module}/scripts/06-ssl-certificates.sh"
  etag   = filemd5("${path.module}/scripts/06-ssl-certificates.sh")

  tags = {
    Name = "ssl-certificates-script"
  }
}

resource "aws_s3_object" "finalize_script" {
  bucket = aws_s3_bucket.scripts.id
  key    = "99-finalize.sh"
  source = "${path.module}/scripts/99-finalize.sh"
  etag   = filemd5("${path.module}/scripts/99-finalize.sh")

  tags = {
    Name = "finalize-script"
  }
}

# Operational scripts (deployed to /usr/local/bin)
resource "aws_s3_object" "deploy_script" {
  bucket = aws_s3_bucket.scripts.id
  key    = "deploy.sh"
  source = "${path.module}/scripts/deploy.sh"
  etag   = filemd5("${path.module}/scripts/deploy.sh")

  tags = {
    Name = "deploy-script"
  }
}

resource "aws_s3_object" "switch_backend_script" {
  bucket = aws_s3_bucket.scripts.id
  key    = "switch-backend.sh"
  source = "${path.module}/scripts/switch-backend.sh"
  etag   = filemd5("${path.module}/scripts/switch-backend.sh")

  tags = {
    Name = "switch-backend-script"
  }
}

resource "aws_s3_object" "run_migrations_script" {
  bucket = aws_s3_bucket.scripts.id
  key    = "run-migrations.sh"
  source = "${path.module}/scripts/run-migrations.sh"
  etag   = filemd5("${path.module}/scripts/run-migrations.sh")

  tags = {
    Name = "run-migrations-script"
  }
}

resource "aws_s3_object" "backup_certificates_script" {
  bucket = aws_s3_bucket.scripts.id
  key    = "backup-certificates.sh"
  source = "${path.module}/scripts/backup-certificates.sh"
  etag   = filemd5("${path.module}/scripts/backup-certificates.sh")

  tags = {
    Name = "backup-certificates-script"
  }
}
