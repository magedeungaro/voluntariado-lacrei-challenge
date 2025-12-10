output "ecr_repository_url" {
  description = "ECR repository URL for production"
  value       = module.lacrei_infra.ecr_repository_url
}

output "ec2_instance_id" {
  description = "EC2 instance ID (use with SSM) - Add to GitHub Secrets as EC2_INSTANCE_ID"
  value       = module.lacrei_infra.ec2_instance_id
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = module.lacrei_infra.rds_endpoint
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.lacrei_infra.vpc_id
}

output "ssm_port_forward_command" {
  description = "Command to create SSM port forwarding session"
  value       = module.lacrei_infra.ssm_port_forward_command
}

output "deployment_commands" {
  description = "Commands to deploy and switch blue/green"
  value       = module.lacrei_infra.deployment_commands
}

output "github_secrets_reminder" {
  description = "Reminder to add EC2 instance ID to GitHub Secrets"
  value       = <<-EOT
    
    ============================================================
    IMPORTANT: Add this to your GitHub Repository Secrets:
    
    Secret Name: EC2_INSTANCE_ID
    Secret Value: ${module.lacrei_infra.ec2_instance_id}
    ============================================================
  EOT
}
