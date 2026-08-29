provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "HV-B16A-MultiCloud-Mavericks"
      Repository  = "hv-ecommerce-devops"
    }
  }
}