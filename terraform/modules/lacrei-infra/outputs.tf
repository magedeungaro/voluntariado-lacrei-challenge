output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = local.ecr_repository_url
}

output "ec2_instance_id" {
  description = "EC2 instance ID (use with SSM)"
  value       = aws_instance.app.id
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.main.address
}

output "rds_port" {
  description = "RDS PostgreSQL port"
  value       = aws_db_instance.main.port
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

# Judge SSM access credentials
output "judge_access_key_id" {
  description = "Judge IAM user access key ID"
  value       = var.create_ssm_judge_user ? aws_iam_access_key.judge[0].id : null
  sensitive   = true
}

output "judge_secret_access_key" {
  description = "Judge IAM user secret access key"
  value       = var.create_ssm_judge_user ? aws_iam_access_key.judge[0].secret : null
  sensitive   = true
}

# SSM commands for judge
output "ssm_port_forward_command" {
  description = "Command for judge to create SSM port forwarding session"
  value       = <<-EOT
    # Install AWS CLI and session-manager-plugin first
    # Then run:
    aws ssm start-session \
      --target ${aws_instance.app.id} \
      --document-name AWS-StartPortForwardingSession \
      --parameters '{"portNumber":["80"],"localPortNumber":["8080"]}' \
      --region ${var.aws_region}
    
    # Then open http://localhost:8080 in browser
  EOT
}

# Deployment commands
output "deployment_commands" {
  description = "Commands to deploy and switch blue/green"
  value       = <<-EOT
    # 1. Build and push image to ECR:
    aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${local.ecr_repository_url}
    docker build -t ${local.ecr_repository_url}:latest .
    docker push ${local.ecr_repository_url}:latest

    # 2. Deploy to blue slot (via SSM):
    aws ssm send-command \
      --instance-ids ${aws_instance.app.id} \
      --document-name "AWS-RunShellScript" \
      --parameters 'commands=["sudo /usr/local/bin/deploy.sh blue latest"]' \
      --region ${var.aws_region}

    # 3. Run migrations (via SSM):
    aws ssm send-command \
      --instance-ids ${aws_instance.app.id} \
      --document-name "AWS-RunShellScript" \
      --parameters 'commands=["sudo /usr/local/bin/run-migrations.sh"]' \
      --region ${var.aws_region}

    # 4. Switch traffic to blue:
    aws ssm send-command \
      --instance-ids ${aws_instance.app.id} \
      --document-name "AWS-RunShellScript" \
      --parameters 'commands=["sudo /usr/local/bin/switch-backend.sh blue"]' \
      --region ${var.aws_region}
  EOT
}
