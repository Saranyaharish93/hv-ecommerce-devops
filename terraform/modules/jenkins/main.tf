# Latest Ubuntu 26.04 LTS AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-resolute-26.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# 1. SSH Key Pair Generation for Ansible Access
resource "tls_private_key" "jenkins_ssh_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "jenkins" {
  key_name   = "${var.project_name}-${var.environment}-jenkins-key"
  public_key = tls_private_key.jenkins_ssh_key.public_key_openssh

  tags = {
    Name = "${var.project_name}-jenkins-ssh-key"
  }
}

# Save the private key locally for Ansible to use (Sprint 3)
resource "local_file" "jenkins_private_key" {
  content         = tls_private_key.jenkins_ssh_key.private_key_pem
  filename        = "${path.root}/../ansible/jenkins_key.pem"
  file_permission = "0400"
}

# 2. IAM Role & Instance Profile for Jenkins
resource "aws_iam_role" "jenkins" {
  name = "${var.project_name}-${var.environment}-jenkins-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })

  tags = {
    Name = "${var.project_name}-jenkins-iam-role"
  }
}

resource "aws_iam_role_policy_attachment" "jenkins_admin" {
  role       = aws_iam_role.jenkins.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_iam_instance_profile" "jenkins" {
  name = "${var.project_name}-${var.environment}-jenkins-profile"
  role = aws_iam_role.jenkins.name
}

# 3. Jenkins EC2 Instance in Public Subnet
resource "aws_instance" "jenkins" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = var.public_subnet_id
  vpc_security_group_ids = [var.security_group_id]
  iam_instance_profile   = aws_iam_instance_profile.jenkins.name
  key_name               = aws_key_pair.jenkins.key_name

  root_block_device {
    volume_size           = 30
    volume_type           = "gp3"
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "${var.project_name}-jenkins-root-vol"
    }
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-jenkins-server"
    Role = "CI-CD-Controller"
  }
}