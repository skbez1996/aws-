# Terraform Infrastructure

This directory contains Terraform configurations for AWS infrastructure.

## Prerequisites

- Terraform >= 1.0
- AWS CLI configured with valid credentials
- GitHub Secrets configured (for CI/CD):
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_REGION`

## Structure

- `main.tf` - Provider and backend configuration
- `variables.tf` - Input variable definitions
- `s3.tf` - S3 bucket resources
- `outputs.tf` - Output values
- `terraform.tfvars.example` - Example variables file

## Local Usage

1. **Copy and configure variables:**
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   ```

2. **Initialize Terraform:**
   ```bash
   terraform init
   ```

3. **Plan changes:**
   ```bash
   terraform plan
   ```

4. **Apply changes:**
   ```bash
   terraform apply
   ```

5. **View outputs:**
   ```bash
   terraform output
   ```

## CI/CD Deployment

The infrastructure is automatically deployed via GitHub Actions when:
- Changes are pushed to `main` branch in the `terraform/` directory
- Can also be manually triggered via workflow_dispatch

### Workflow Steps:
1. **Format Check** - Validates Terraform formatting
2. **Init** - Initializes Terraform
3. **Validate** - Validates configuration
4. **Plan** - Creates execution plan
5. **Apply** - Applies changes (only on main branch)

### Pull Request Workflow:
- On PRs, the workflow runs plan and comments the results
- No changes are applied until merged to main

## Customization

Edit `terraform.tfvars` or set variables in the workflow to customize:
- `bucket_name` - S3 bucket name prefix
- `aws_region` - AWS region
- `environment` - Environment name (dev, staging, prod)
- `enable_versioning` - Enable bucket versioning
- `enable_encryption` - Enable bucket encryption

## Current Resources

- **S3 Bucket** with:
  - Versioning enabled (configurable)
  - Server-side encryption (AES256)
  - Public access blocked
  - Proper tagging

## Outputs

After applying, you'll see:
- `bucket_name` - The full bucket name
- `bucket_arn` - ARN of the bucket
- `bucket_region` - Region where bucket is created
- `bucket_domain_name` - Domain name of the bucket
