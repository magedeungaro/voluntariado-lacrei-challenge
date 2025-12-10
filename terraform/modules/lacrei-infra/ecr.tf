# ECR Repository (shared across environments - only created in production)
resource "aws_ecr_repository" "app" {
  count                = var.create_ecr ? 1 : 0
  name                 = var.project_name
  image_tag_mutability = "MUTABLE"
  force_delete         = true  # Allow deletion even with images

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name = "${var.project_name}-ecr"
  }
}

# Data source to reference existing ECR (used when create_ecr is false)
data "aws_ecr_repository" "existing" {
  count = var.create_ecr ? 0 : 1
  name  = var.project_name
}

# Local to get the ECR repository URL regardless of whether it was created or referenced
locals {
  ecr_repository_url = var.create_ecr ? aws_ecr_repository.app[0].repository_url : data.aws_ecr_repository.existing[0].repository_url
}

# ECR Lifecycle Policy (keep only last 10 images) - only when creating ECR
resource "aws_ecr_lifecycle_policy" "app" {
  count      = var.create_ecr ? 1 : 0
  repository = aws_ecr_repository.app[0].name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
