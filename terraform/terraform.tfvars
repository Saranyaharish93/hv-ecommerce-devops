aws_region                   = "us-east-1"
environment                  = "prod"
project_name                 = "lumora-ecommerce"
vpc_cidr                     = "10.0.0.0/16"
availability_zones           = ["us-east-1a", "us-east-1b"]
public_subnet_cidrs          = ["10.0.1.0/24", "10.0.2.0/24"]
private_compute_subnet_cidrs = ["10.0.48.0/20", "10.0.64.0/20"]
restricted_subnet_cidrs      = ["10.0.31.0/24", "10.0.32.0/24"]
eks_cluster_version          = "1.36"

# Set to true when starting Sprint 4 (Kubernetes deployment)
# Set to false to destroy EKS and save ~$140/month when not in use
enable_eks = false

# Set to true together with enable_eks — NAT Gateway is only needed for EKS worker nodes
# Set to false to destroy NAT Gateway and save ~$33/month when EKS is not running
enable_nat_gateway = false

# Set FinOps budget variables
monthly_budget_limit = "25"
budget_notification_emails = ["rinku.chn07@gmail.com",
                              "thiagarajanb@gmail.com",
                              "saranya.smiles55@gmail.com",
                              "nivedhasaibaba@gmail.com" 
                             ]