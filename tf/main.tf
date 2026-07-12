# tf/main.tf
# Core Terraform Provider configurations, global variables, and AWS Certificate Manager configurations.

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
}

# Main home provider (e.g. eu-west-2 London or us-west-2 Oregon)
provider "aws" {
  region = var.aws_region
}

# Secondary provider targeting us-east-1 (strictly required for CloudFront SSL ACM certificates)
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

variable "aws_region" {
  type        = string
  default     = "eu-west-2"
  description = "The home AWS region where core serverless, storage, and secrets will be provisioned."
}

variable "domain_name" {
  type        = string
  default     = "emf.harvinderatwal.com"
  description = "Custom domain used to distribute the static websites and dashboards."
}

# ACM SSL Certificate for CloudFront custom domain mapping (created in us-east-1)
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
