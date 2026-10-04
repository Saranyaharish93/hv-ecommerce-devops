# ==============================================================================
# AWS Secrets Manager: Production Application & Database Credentials
# ==============================================================================

# 1. Generate cryptographically strong random passwords
resource "random_password" "flask_secret_key" {
  length  = 32
  special = false
}

resource "random_password" "admin_password" {
  length           = 16
  special          = true
  override_special = "!@#$%"
}

resource "random_password" "mongo_root_password" {
  length           = 16
  special          = true
  override_special = "!@#$%"
}

# 2. Define the Secret in AWS Secrets Manager
resource "aws_secretsmanager_secret" "app_secrets" {
  name                    = "${var.project_name}-${var.environment}-secrets"
  description             = "Production application and MongoDB credentials for Lumora E-Commerce"
  recovery_window_in_days = 0 # FinOps: Allows immediate deletion during capstone teardown without holding costs

  tags = {
    Name        = "${var.project_name}-${var.environment}-secrets"
    Environment = var.environment
    CostCenter  = "Multicloud-Mavericks"
  }
}

# 3. Store the Secret Values as a JSON string
resource "aws_secretsmanager_secret_version" "app_secrets_val" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    SECRET_KEY                 = random_password.flask_secret_key.result
    ADMIN_PASSWORD             = random_password.admin_password.result
    MONGO_INITDB_ROOT_PASSWORD = random_password.mongo_root_password.result
  })
}

# 4. IAM Policy to allow EKS worker nodes to fetch this secret
resource "aws_iam_policy" "secrets_read_policy" {
  name        = "${var.project_name}-${var.environment}-secrets-read-policy"
  description = "Allows EKS worker nodes to read ${aws_secretsmanager_secret.app_secrets.name}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = aws_secretsmanager_secret.app_secrets.arn
      }
    ]
  })
}

# 5. Attach the policy to EKS worker node role (conditional on EKS being enabled)
resource "aws_iam_role_policy_attachment" "eks_secrets_read" {
  count      = var.enable_eks ? 1 : 0
  role       = module.eks[0].node_iam_role_name
  policy_arn = aws_iam_policy.secrets_read_policy.arn
}