terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Store Terraform state in S3 (optional but recommended)
  # Uncomment after creating the state bucket manually
  # backend "s3" {
  #   bucket = "terraform-state-bucket-name"
  #   key    = "aws-infra/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region = var.aws_region
}
