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
}

# Main home provider (e.g. eu-west-2 London)
provider "aws" {
  region  = var.aws_region
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
