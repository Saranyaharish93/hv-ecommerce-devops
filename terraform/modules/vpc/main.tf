# ==============================================================================
# Task 8: Provision AWS VPC
# ==============================================================================
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.project_name}-${var.environment}-vpc"
  }
}

# ==============================================================================
# Task 10: Internet Gateway (IGW)
# ==============================================================================
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-${var.environment}-igw"
  }
}

# ==============================================================================
# Task 9: 3-Tier Subnets (Public, Private Compute, Restricted)
# ==============================================================================

# 1. Public Subnets (ALB, NAT Gateway, Jenkins EC2)
resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name                                                           = "${var.project_name}-${var.environment}-public-${var.availability_zones[count.index]}"
    Tier                                                           = "Public"
    "kubernetes.io/role/elb"                                       = "1"
    "kubernetes.io/cluster/${var.project_name}-${var.environment}" = "shared"
  }
}

# 2. Private Compute Subnets (EKS Worker Nodes, Flask Pods)
resource "aws_subnet" "private_compute" {
  count             = length(var.private_compute_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_compute_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name                                                           = "${var.project_name}-${var.environment}-private-compute-${var.availability_zones[count.index]}"
    Tier                                                           = "Private-Compute"
    "kubernetes.io/role/internal-elb"                              = "1"
    "kubernetes.io/cluster/${var.project_name}-${var.environment}" = "shared"
  }
}

# 3. Restricted Subnets (MongoDB - Isolated, Zero Internet)
resource "aws_subnet" "restricted" {
  count             = length(var.restricted_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.restricted_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "${var.project_name}-${var.environment}-restricted-${var.availability_zones[count.index]}"
    Tier = "Restricted-Data"
  }
}

# ==============================================================================
# Task 10: NAT Gateway & Elastic IP
# Controlled by enable_nat_gateway — destroy when EKS is not running (~$33/month)
# ==============================================================================
resource "aws_eip" "nat" {
  count      = var.enable_nat_gateway ? 1 : 0
  domain     = "vpc"
  depends_on = [aws_internet_gateway.igw]

  tags = {
    Name = "${var.project_name}-${var.environment}-nat-eip"
  }
}

resource "aws_nat_gateway" "nat" {
  count         = var.enable_nat_gateway ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public[0].id
  depends_on    = [aws_internet_gateway.igw]

  tags = {
    Name = "${var.project_name}-${var.environment}-nat-gw"
  }
}

# ==============================================================================
# Task 10: Route Tables & Subnet Associations
# ==============================================================================

# Public Route Table (0.0.0.0/0 -> IGW)
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Private Compute Route Table
# When NAT is enabled: 0.0.0.0/0 -> NAT Gateway
# When NAT is disabled: local only (no internet — EKS not running)
resource "aws_route_table" "private_compute" {
  vpc_id = aws_vpc.main.id

  dynamic "route" {
    for_each = var.enable_nat_gateway ? [1] : []
    content {
      cidr_block     = "0.0.0.0/0"
      nat_gateway_id = aws_nat_gateway.nat[0].id
    }
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-private-compute-rt"
  }
}

resource "aws_route_table_association" "private_compute" {
  count          = length(aws_subnet.private_compute)
  subnet_id      = aws_subnet.private_compute[count.index].id
  route_table_id = aws_route_table.private_compute.id
}

# Restricted Route Table (Local only — 🚫 Zero Internet)
resource "aws_route_table" "restricted" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-${var.environment}-restricted-rt"
  }
}

resource "aws_route_table_association" "restricted" {
  count          = length(aws_subnet.restricted)
  subnet_id      = aws_subnet.restricted[count.index].id
  route_table_id = aws_route_table.restricted.id
}