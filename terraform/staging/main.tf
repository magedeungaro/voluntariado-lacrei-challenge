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

  # Remote state for staging
  backend "s3" {
    bucket = "lacrei-terraform-state-magedeungaro"
    key    = "staging/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "lacrei-saude"
      Environment = "staging"
      ManagedBy   = "terraform"
    }
  }
}

provider "random" {}

module "lacrei_infra" {
  source = "../modules/lacrei-infra"

  aws_region        = var.aws_region
  environment       = "staging"
  project_name      = var.project_name
  instance_type     = var.instance_type
  db_name           = var.db_name
  db_user           = var.db_user
  db_password       = var.db_password
  django_secret_key = var.django_secret_key
  vpc_cidr          = var.vpc_cidr
  create_ecr        = false # Use existing ECR from production
  domain_name       = var.domain_name
  ssl_email         = var.ssl_email
}
