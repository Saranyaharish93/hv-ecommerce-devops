# ==============================================================================
# Task 3: Create AWS ECR Repository
# Stores immutable, tagged Docker images for the Lumora Flask application.
# ==============================================================================

resource "aws_ecr_repository" "lumora_flask" {
  name                 = "${var.project_name}-flask"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-ecr"
  }
}

# ==============================================================================
# Lifecycle Policy — keep last 10 tagged images, expire untagged after 1 day
# ==============================================================================
resource "aws_ecr_lifecycle_policy" "lumora_flask" {
  repository = aws_ecr_repository.lumora_flask.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Expire untagged images after 1 day"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 1
        }
        action = { type = "expire" }
      },
      {
        rulePriority = 2
        description  = "Keep only the last 10 tagged images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v", "build-"]
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = { type = "expire" }
      }
    ]
  })
}

# ==============================================================================
# Repository Policy — allow Jenkins EC2 role to push/pull images
# ==============================================================================
resource "aws_ecr_repository_policy" "lumora_flask" {
  repository = aws_ecr_repository.lumora_flask.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowJenkinsPushPull"
        Effect = "Allow"
        Principal = {
          AWS = var.jenkins_role_arn
        }
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:DescribeRepositories",
          "ecr:ListImages"
        ]
      }
    ]
  })
}
