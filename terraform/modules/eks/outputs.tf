output "cluster_name" {
  description = "EKS cluster name — used in kubectl and Jenkins pipeline"
  value       = aws_eks_cluster.main.name
}

output "cluster_endpoint" {
  description = "EKS API server endpoint — used by kubectl and Terraform kubernetes provider"
  value       = aws_eks_cluster.main.endpoint
}

output "cluster_certificate_authority" {
  description = "Base64-encoded CA certificate for the EKS cluster"
  value       = aws_eks_cluster.main.certificate_authority[0].data
  sensitive   = true
}

output "cluster_version" {
  description = "Kubernetes version running on the EKS control plane"
  value       = aws_eks_cluster.main.version
}

output "node_group_name" {
  description = "EKS managed node group name"
  value       = aws_eks_node_group.main.node_group_name
}

output "node_group_status" {
  description = "Current status of the EKS managed node group"
  value       = aws_eks_node_group.main.status
}

output "cluster_iam_role_arn" {
  description = "IAM role ARN of the EKS control plane"
  value       = aws_iam_role.eks_cluster.arn
}

output "node_iam_role_arn" {
  description = "IAM role ARN of the EKS worker nodes"
  value       = aws_iam_role.eks_node_group.arn
}

output "oidc_provider_arn" {
  description = "OIDC provider ARN — used for IAM Roles for Service Accounts (IRSA)"
  value       = aws_iam_openid_connect_provider.eks.arn
}

output "oidc_provider_url" {
  description = "OIDC provider URL — used when creating IRSA trust policies"
  value       = aws_iam_openid_connect_provider.eks.url
}

output "node_iam_role_name" {
  description = "IAM role name of the EKS worker nodes"
  value       = aws_iam_role.eks_node_group.name
}