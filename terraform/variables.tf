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
  default     = ["10.0.10.0/20", "10.0.20.0/20"]
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