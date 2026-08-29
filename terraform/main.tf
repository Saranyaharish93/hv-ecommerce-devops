# ==============================================================================
# Lumora E-Commerce DevOps Platform - Root Terraform Configuration
# ==============================================================================

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "HV-B16A-MultiCloud-Mavericks"
  }
}

# Module declarations (VPC, Security Groups, ECR, EKS, etc.) will be connected
# here as each sprint task is implemented.