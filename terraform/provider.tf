terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }

  # Uncomment for remote state (recommended for team/production)
  # backend "s3" {
  #   bucket = "your-terraform-state-bucket"
  #   key    = "lacrei-saude/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "lacrei-saude"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

provider "random" {}
