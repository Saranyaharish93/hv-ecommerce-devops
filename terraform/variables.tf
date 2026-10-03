variable "aws_region" {
  description = "AWS region for provisioning infrastructure"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name (e.g. dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Project identifier used in resource names"
  type        = string
  default     = "lumora-ecommerce"
}

variable "vpc_cidr" {
  description = "CIDR block for the AWS VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of Availability Zones to use across the VPC"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets (ALB, NAT Gateways)"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_compute_subnet_cidrs" {
  description = "CIDR blocks for private compute subnets (EKS Nodes, Flask Pods, Jenkins)"
  type        = list(string)
  default     = ["10.0.48.0/20", "10.0.64.0/20"]
}

variable "restricted_subnet_cidrs" {
  description = "CIDR blocks for restricted database subnets (MongoDB, Databases)"
  type        = list(string)
  default     = ["10.0.31.0/24", "10.0.32.0/24"]
}

variable "eks_cluster_version" {
  description = "The Kubernetes control plane version for AWS EKS"
  type        = string
  default     = "1.36"
}

variable "enable_nat_gateway" {
  description = "Set to true to provision NAT Gateway. Set to false to destroy and save ~$33/month when EKS is not running."
  type        = bool
  default     = false
}

variable "enable_eks" {
  description = "Set to true to provision EKS cluster and node group. Set to false to destroy EKS and save costs when not in use (Sprint 4+)."
  type        = bool
  default     = false
}

variable "monthly_budget_limit" {
  description = "FinOps: Monthly budget ceiling in USD"
  type        = string
  default     = "25"
}

variable "budget_notification_emails" {
  description = "FinOps: Email addresses to receive budget threshold alerts"
  type        = list(string)
  default = ["rinku.chn07@gmail.com",
    "thiagarajanb@gmail.com",
    "saranya.smiles55@gmail.com",
    "nivedhasaibaba@gmail.com"
  ]
}