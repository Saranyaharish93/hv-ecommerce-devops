variable "project_name" {
  description = "Project identifier used in resource names"
  type        = string
}

variable "environment" {
  description = "Deployment environment name (e.g. dev, staging, prod)"
  type        = string
}

variable "jenkins_role_arn" {
  description = "IAM Role ARN of the Jenkins EC2 instance — granted push/pull access to ECR"
  type        = string
}
