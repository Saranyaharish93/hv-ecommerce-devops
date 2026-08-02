module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.13.0"
  name = "${var.cluster_name}-vpc"
  cidr = "10.0.0.0/16"
  azs = ["ap-south-1a", "ap-south-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]
  enable_nat_gateway = true
  single_nat_gateway = true
  enable_dns_hostnames = true
  public_subnet_tags = { "kubernetes.io/role/elb" = 1 }
  private_subnet_tags = { "kubernetes.io/role/internal-elb" = 1 }
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.24.0"
  cluster_name = var.cluster_name
  cluster_version = "1.30"
  cluster_endpoint_public_access = true
  vpc_id = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  eks_managed_node_groups = {
    default = {
      instance_types = ["t3.medium"]
      min_size = 2
      max_size = 4
      desired_size = 2
    }
  }
}
