output "jenkins_iam_role_arn" {
  description = "IAM Role ARN of the Jenkins EC2 instance — used to grant ECR push/pull access"
  value       = aws_iam_role.jenkins.arn
}

output "jenkins_instance_id" {
  description = "The EC2 Instance ID of the Jenkins Server"
  value       = aws_instance.jenkins.id
}

output "ssh_private_key_path" {
  description = "Path to the private key for Ansible connections"
  value       = local_file.jenkins_private_key.filename
}

output "jenkins_public_ip" {
  description = "Permanent Elastic IP for Jenkins Web UI and Ansible SSH"
  value       = aws_eip.jenkins.public_ip
}

output "ansible_ssh_command" {
  description = "SSH command to connect to Jenkins Server using the permanent Elastic IP"
  value       = "ssh -i ${local_file.jenkins_private_key.filename} ubuntu@${aws_eip.jenkins.public_ip}"
}