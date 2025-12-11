variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
}

variable "environment" {
  description = "Environment name (staging, production)"
  type        = string
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
}

variable "db_user" {
  description = "PostgreSQL database user"
  type        = string
}

variable "db_password" {
  description = "PostgreSQL database password"
  type        = string
  sensitive   = true
}

variable "django_secret_key" {
  description = "Django SECRET_KEY"
  type        = string
  sensitive   = true
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "create_ecr" {
  description = "Create ECR repository (set to false for staging to use existing production ECR)"
  type        = bool
  default     = true
}

variable "domain_name" {
  description = "Domain name for the application (e.g., api.magenifica.dev)"
  type        = string
  default     = "_"
}

variable "ssl_email" {
  description = "Email address for SSL certificate notifications from Let's Encrypt"
  type        = string
  default     = "admin@example.com"
}
