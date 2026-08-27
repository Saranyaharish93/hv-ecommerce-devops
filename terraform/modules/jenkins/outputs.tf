output "jenkins_instance_id" {
  description = "The EC2 Instance ID of the Jenkins Server"
  value       = aws_instance.jenkins.id
}

output "jenkins_public_ip" {
  description = "The Public IP for Ansible SSH and Web UI"
  value       = aws_instance.jenkins.public_ip
}

output "ssh_private_key_path" {
  description = "Path to the private key for Ansible connections"
  value       = local_file.jenkins_private_key.filename
}

output "ansible_ssh_command" {
  description = "Convenient SSH command to test connectivity"
  value       = "ssh -i ${local_file.jenkins_private_key.filename} ubuntu@${aws_instance.jenkins.public_ip}"
}