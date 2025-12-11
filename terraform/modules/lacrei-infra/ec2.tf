# EC2 Instance

resource "aws_instance" "app" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public[0].id
  vpc_security_group_ids      = [aws_security_group.ec2.id]
  iam_instance_profile        = aws_iam_instance_profile.ec2.name
  associate_public_ip_address = false

  root_block_device {
    volume_size           = 30
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = true
  }

  user_data = base64encode(templatefile("${path.module}/templates/user_data.sh", {
    aws_region         = var.aws_region
    ecr_repository_url = local.ecr_repository_url
    db_host            = aws_db_instance.main.address
    db_name            = var.db_name
    db_user            = var.db_user
    db_password        = var.db_password
    django_secret_key  = var.django_secret_key
    project_name       = var.project_name
    environment        = var.environment
    domain_name        = var.domain_name
    ssl_email          = var.ssl_email
  }))

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required" # IMDSv2 required for security
    http_put_response_hop_limit = 1
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-app"
  }

  depends_on = [
    aws_db_instance.main,
    aws_nat_gateway.main
  ]
}

# Elastic IP for stable public IP address
resource "aws_eip" "app" {
  domain = "vpc"

  tags = {
    Name = "${var.project_name}-${var.environment}-eip"
  }
}

# Associate Elastic IP with EC2 instance
resource "aws_eip_association" "app" {
  instance_id   = aws_instance.app.id
  allocation_id = aws_eip.app.id
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ec2/${var.project_name}-${var.environment}"
  retention_in_days = var.environment == "production" ? 30 : 7

  tags = {
    Name = "${var.project_name}-${var.environment}-logs"
  }
}
