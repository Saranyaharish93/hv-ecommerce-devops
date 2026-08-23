terraform {
  # Minimum Terraform version
  required_version = ">= 1.6.0, < 2.0.0"

  required_providers {
    # AWS Provider (Latest v5 series)
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }

    # Kubernetes Provider (for interacting with EKS)
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.28"
    }

    # Helm Provider (for Prometheus, Grafana, AWS LB Controller)
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.13"
    }

    # TLS Provider (for EKS OIDC provider authentication)
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }

    # Random Provider (for unique resource naming)
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}