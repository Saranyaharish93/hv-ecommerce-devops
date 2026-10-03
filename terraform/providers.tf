# terraform/providers.tf
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      # Ownership & Accounting
      Project     = var.project_name
      Environment = var.environment
      Owner       = "MultiCloud-Mavericks"
      CostCenter  = "CAPSTONE-B16A"

      # Technical Context
      ManagedBy  = "Terraform"
      Repository = "hv-ecommerce-devops"

      # FinOps & Governance
      AutoStop      = "true" # Eligible for non-business-hours shutdown
      ProvisionDate = "2026-10-01"
    }
  }
}