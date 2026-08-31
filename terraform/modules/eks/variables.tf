variable "project_name" {
  description = "Project identifier used in resource names"
  type        = string
}

variable "environment" {
  description = "Deployment environment name (e.g. dev, staging, prod)"
  type        = string
}

variable "eks_cluster_version" {
  description = "Kubernetes control plane version for the EKS cluster"
  type        = string
  default     = "1.36"
}

variable "private_compute_subnet_ids" {
  description = "Private compute subnet IDs where EKS worker nodes are placed"
  type        = list(string)
}

variable "public_subnet_ids" {
  description = "Public subnet IDs included in the EKS VPC config for ALB ingress"
  type        = list(string)
}

variable "eks_nodes_security_group_id" {
  description = "Security group ID applied to EKS worker nodes"
  type        = string
}

variable "node_instance_type" {
  description = "EC2 instance type for EKS managed node group workers"
  type        = string
  default     = "t3.medium"
}

variable "node_desired_size" {
  description = "Desired number of worker nodes in the node group"
  type        = number
  default     = 2
}

variable "node_min_size" {
  description = "Minimum number of worker nodes (used by HPA scale-in)"
  type        = number
  default     = 2
}

variable "node_max_size" {
  description = "Maximum number of worker nodes (used by HPA scale-out)"
  type        = number
  default     = 4
}
