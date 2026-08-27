# ==============================================================================
# Global & Environment Outputs
# ==============================================================================
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

# ==============================================================================
# VPC Module Outputs (Sprint 1 #8, #9, #10)
# ==============================================================================
output "vpc_id" {
  description = "The Primary VPC ID"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public Subnet IDs (ALB, NAT GW, Jenkins)"
  value       = module.vpc.public_subnet_ids
}

output "private_compute_subnet_ids" {
  description = "Private Compute Subnet IDs (EKS Nodes & Pods)"
  value       = module.vpc.private_compute_subnet_ids
}

output "restricted_subnet_ids" {
  description = "Restricted Subnet IDs (MongoDB)"
  value       = module.vpc.restricted_subnet_ids
}

output "nat_gateway_ip" {
  description = "Elastic IP of the NAT Gateway"
  value       = module.vpc.nat_gateway_ip
}

# ==============================================================================
# Security Group Outputs (Sprint 1 #11)
# ==============================================================================
output "alb_sg_id" {
  description = "Security Group ID for ALB"
  value       = module.security_groups.alb_security_group_id
}

output "jenkins_sg_id" {
  description = "Security Group ID for Jenkins"
  value       = module.security_groups.jenkins_security_group_id
}

output "eks_nodes_sg_id" {
  description = "Security Group ID for EKS Nodes"
  value       = module.security_groups.eks_nodes_security_group_id
}

output "mongodb_sg_id" {
  description = "Security Group ID for MongoDB"
  value       = module.security_groups.mongodb_security_group_id
}

# ==============================================================================
# Jenkins EC2 Outputs (Sprint 2 #4 - for Ansible in Sprint 3)
# ==============================================================================
output "jenkins_instance_id" {
  description = "EC2 Instance ID of the Jenkins Server"
  value       = module.jenkins.jenkins_instance_id
}

output "jenkins_public_ip" {
  description = "Public IP of the Jenkins Controller"
  value       = module.jenkins.jenkins_public_ip
}

output "ansible_ssh_command" {
  description = "SSH Command to connect to Jenkins Server"
  value       = module.jenkins.ansible_ssh_command
}