output "repository_url" {
  description = "Full ECR repository URL for docker push/pull (used in Jenkins pipeline)"
  value       = aws_ecr_repository.lumora_flask.repository_url
}

output "repository_name" {
  description = "ECR repository name"
  value       = aws_ecr_repository.lumora_flask.name
}

output "repository_arn" {
  description = "ECR repository ARN"
  value       = aws_ecr_repository.lumora_flask.arn
}

output "registry_id" {
  description = "AWS account ID associated with the ECR registry"
  value       = aws_ecr_repository.lumora_flask.registry_id
}
