variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "environment" {
  description = "The environment name"
  type        = string
}

variable "public_subnet_id" {
  description = "Subnet ID where Jenkins will be deployed"
  type        = string
}

variable "security_group_id" {
  description = "Security Group ID for Jenkins"
  type        = string
}

variable "instance_type" {
  description = "EC2 Instance type"
  type        = string
  default     = "t3.small"
}