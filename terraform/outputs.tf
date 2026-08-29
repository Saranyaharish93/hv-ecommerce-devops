output "aws_region" {
  description = "AWS Region configured for deployment"
  value       = var.aws_region
}

output "environment" {
  description = "Target deployment environment"
  value       = var.environment
}

output "project_name" {
  description = "Project identifier"
  value       = var.project_name
}

output "vpc_cidr" {
  description = "The Primary CIDR block of the VPC"
  value       = var.vpc_cidr
}

output "availability_zones" {
  description = "Availability Zones used in the VPC"
  value       = var.availability_zones
}

output "public_subnet_cidrs" {
  description = "Public Subnet CIDR allocations"
  value       = var.public_subnet_cidrs
}

output "private_compute_subnet_cidrs" {
  description = "Private Compute Subnet CIDR allocations (EKS & Apps)"
  value       = var.private_compute_subnet_cidrs
}

output "restricted_subnet_cidrs" {
  description = "Restricted Database Subnet CIDR allocations (MongoDB)"
  value       = var.restricted_subnet_cidrs
}

output "eks_cluster_version" {
  description = "Kubernetes control plane version configured for EKS"
  value       = var.eks_cluster_version
}