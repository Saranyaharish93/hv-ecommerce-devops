output "alb_security_group_id" {
  description = "Security Group ID for ALB"
  value       = aws_security_group.alb.id
}

output "jenkins_security_group_id" {
  description = "Security Group ID for Jenkins"
  value       = aws_security_group.jenkins.id
}

output "eks_nodes_security_group_id" {
  description = "Security Group ID for EKS Nodes"
  value       = aws_security_group.eks_nodes.id
}

output "mongodb_security_group_id" {
  description = "Security Group ID for MongoDB"
  value       = aws_security_group.mongodb.id
}