variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "environment" {
  description = "The environment name"
  type        = string
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC"
  type        = string
}

variable "availability_zones" {
  description = "List of Availability Zones"
  type        = list(string)
}

variable "public_subnet_cidrs" {
  description = "List of Public Subnet CIDRs"
  type        = list(string)
}

variable "private_compute_subnet_cidrs" {
  description = "List of Private Compute Subnet CIDRs"
  type        = list(string)
}
variable "restricted_subnet_cidrs" { type = list(string) }