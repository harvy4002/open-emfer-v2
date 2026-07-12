# tf/main.tf
# Core Terraform Provider configurations, global variables, and home region provider bindings.

terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }

  # S3 Remote State Backend to sync state between your local machine and GitHub Actions (complying with Principle III)
  backend "s3" {
    bucket  = "open-emfer-v2-production-tfstate-harvy"
    key     = "production/terraform.tfstate"
    region  = "eu-west-2"
    profile = "open-emfer"
  }
}

# Main home provider (e.g. eu-west-2 London)
provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

# Secondary provider targeting us-east-1 (strictly required for CloudFront SSL ACM certificates, Path B)
provider "aws" {
  alias   = "us_east_1"
  region  = "us-east-1"
  profile = var.aws_profile
}

variable "aws_region" {
  type        = string
  default     = "eu-west-2"
  description = "The home AWS region where core serverless, storage, and secrets will be provisioned."
}

variable "aws_profile" {
  type        = string
  default     = "open-emfer"
  description = "The local AWS CLI named profile used to authenticate Terraform operations."
}

variable "domain_name" {
  type        = string
  default     = "emf.harvinderatwal.com"
  description = "Custom domain used to distribute the static websites and dashboards."
}

# ACM SSL Certificate for CloudFront custom domain mapping (created in us-east-1, Path B)
resource "aws_acm_certificate" "cert" {
  provider          = aws.us_east_1
  domain_name       = var.domain_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Environment = "production"
    Project     = "open-emfer-v2"
  }
}
