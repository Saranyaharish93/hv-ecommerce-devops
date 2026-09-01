output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_compute_subnet_ids" {
  description = "IDs of the private compute subnets"
  value       = aws_subnet.private_compute[*].id
}

output "restricted_subnet_ids" {
  description = "IDs of the restricted data subnets"
  value       = aws_subnet.restricted[*].id
}

output "nat_gateway_ip" {
  description = "Public Elastic IP of the NAT Gateway (empty when enable_nat_gateway=false)"
  value       = var.enable_nat_gateway ? aws_eip.nat[0].public_ip : "NAT Gateway not provisioned (enable_nat_gateway=false)"
}