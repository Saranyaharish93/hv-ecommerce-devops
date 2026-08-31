# ==============================================================================
# Lumora E-Commerce DevOps Platform - Root Orchestration
# ==============================================================================

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "HV-B16A-MultiCloud-Mavericks"
  }
}

# 1. 3-Tier VPC Module (Sprint 1 #8, #9, #10)
module "vpc" {
  source                       = "./modules/vpc"
  project_name                 = var.project_name
  environment                  = var.environment
  vpc_cidr                     = var.vpc_cidr
  availability_zones           = var.availability_zones
  public_subnet_cidrs          = var.public_subnet_cidrs
  private_compute_subnet_cidrs = var.private_compute_subnet_cidrs
  restricted_subnet_cidrs      = var.restricted_subnet_cidrs
}

# 2. Security Groups Module (Sprint 1 #11)
module "security_groups" {
  source       = "./modules/security_groups"
  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
}

# 3. ECR Repository (Sprint 1 #3)
module "ecr" {
  source           = "./modules/ecr"
  project_name     = var.project_name
  environment      = var.environment
  jenkins_role_arn = module.jenkins.jenkins_iam_role_arn
}

# 4. EKS Cluster & Managed Node Group (Sprint 2 #12, #13)
module "eks" {
  source                      = "./modules/eks"
  project_name                = var.project_name
  environment                 = var.environment
  eks_cluster_version         = var.eks_cluster_version
  private_compute_subnet_ids  = module.vpc.private_compute_subnet_ids
  public_subnet_ids           = module.vpc.public_subnet_ids
  eks_nodes_security_group_id = module.security_groups.eks_nodes_security_group_id
  node_instance_type          = "t3.medium"
  node_desired_size           = 2
  node_min_size               = 2
  node_max_size               = 4
}

# 5. Jenkins EC2 Server Provisioning (Sprint 2 #4)
module "jenkins" {
  source            = "./modules/jenkins"
  project_name      = var.project_name
  environment       = var.environment
  public_subnet_id  = module.vpc.public_subnet_ids[0]
  security_group_id = module.security_groups.jenkins_security_group_id
  instance_type     = "t3.medium"
}