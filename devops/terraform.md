# Infrastructure as Code with Terraform

This document provides a comprehensive technical reference for the Infrastructure as Code (IaC) architecture designed and provisioned with Terraform for the Lumora E-Commerce platform.

---

## Table of Contents

1. [IaC Philosophy and Design Patterns](#1-iac-philosophy-and-design-patterns)
2. [Modular Repository Architecture](#2-modular-repository-architecture)
3. [AWS 3-Tier Network Topology (VPC) with In-Context Proof](#3-aws-3-tier-network-topology-vpc-with-in-context-proof)
4. [State Management and Native S3 Locking with In-Context Proof](#4-state-management-and-native-s3-locking-with-in-context-proof)
5. [Security Groups and Least-Privilege Boundaries](#5-security-groups-and-least-privilege-boundaries)
6. [Secrets Management and AWS Budgets with In-Context Proof](#6-secrets-management-and-aws-budgets-with-in-context-proof)
7. [FinOps Cost Toggles and Plan Execution Proof](#7-finops-cost-toggles-and-plan-execution-proof)

---

## 1. IaC Philosophy and Design Patterns

All infrastructure across AWS is provisioned using HashiCorp Terraform following these engineering principles:

- **100% Declarative**: No manual modifications are allowed in the AWS console ("ClickOps" is strictly prohibited).
- **Modular Reusability**: Infrastructure components are packaged into discrete, decoupled modules with clear inputs (`variables.tf`) and outputs (`outputs.tf`).
- **Blast-Radius Isolation**: Modular resource definitions ensure network changes do not inadvertently invalidate compute or storage resources.
- **Strict State Governance**: State files are encrypted at rest, versioned, and locked against concurrent access.

---

## 2. Modular Repository Architecture

The `terraform/` directory is organized into a root orchestrator and specialized child modules:

```
terraform/
├── main.tf                    # Root orchestrator: invokes child modules and passes outputs
├── variables.tf               # Global input variable declarations and type constraints
├── outputs.tf                 # Global outputs (VPC IDs, ECR URLs, EIPs, Cluster Endpoints)
├── versions.tf                # Required provider constraints (AWS >= 5.0, Random, TLS)
├── providers.tf               # AWS provider configuration and region pinning (us-east-1)
├── terraform.tfvars           # Environment configuration values and FinOps toggles
├── secrets.tf                 # AWS Secrets Manager credentials generation & IAM policies
├── budgets.tf                 # AWS Budgets configuration ($25 limit & email thresholds)
└── modules/
    ├── vpc/                   # 3-Tier VPC, subnets, IGW, NAT GW, and route tables
    ├── security_groups/       # Security group firewall rules for ALB, Jenkins, EKS, Mongo
    ├── ecr/                   # Elastic Container Registry repository & lifecycle policies
    ├── jenkins/               # Jenkins EC2 controller, Elastic IP, and IAM role
    └── eks/                   # EKS cluster control plane, Managed Node Group, IAM roles
```

---

## 3. AWS 3-Tier Network Topology (VPC) with In-Context Proof

The production network implements a 3-tier, multi-AZ layout within the `10.0.0.0/16` CIDR block across availability zones `us-east-1a` and `us-east-1b`:

![AWS VPC / GitOps Platform Architecture](../project_artifacts/Lumora_E-Commerce_GitOps_Platform_v4.jpg)

![End-to-End DevOps & GitOps Architecture](../project_artifacts/Lumora_E-Commerce_Architecture_v4.jpg)

### Subnet Allocation Table

| Subnet Type | Availability Zone | CIDR Block | Available IPs | Workloads Hosted |
| :--- | :--- | :--- | :---: | :--- |
| **Public Subnet 1** | `us-east-1a` | `10.0.1.0/24` | 251 | AWS ALB, Jenkins Controller, NAT Gateway |
| **Public Subnet 2** | `us-east-1b` | `10.0.2.0/24` | 251 | AWS ALB secondary availability zone |
| **Private Compute 1** | `us-east-1a` | `10.0.48.0/20` | 4,091 | EKS Worker Nodes, Flask application pods |
| **Private Compute 2** | `us-east-1b` | `10.0.64.0/20` | 4,091 | EKS Worker Nodes, Flask application pods |
| **Restricted Subnet 1**| `us-east-1a` | `10.0.31.0/24` | 251 | MongoDB StatefulSet database pods |
| **Restricted Subnet 2**| `us-east-1b` | `10.0.32.0/24` | 251 | MongoDB replication / failover pods |

| AWS VPC Network (`10.0.0.0/16`) | Multi-AZ Subnets Configuration |
| :---: | :---: |
| ![AWS VPC Console](../project_artifacts/screenshots/aws/vpc.png) | ![AWS VPC Subnets](../project_artifacts/screenshots/aws/subnets.png) |

| Internet Gateway Configuration | NAT Gateway (High Availability) |
| :---: | :---: |
| ![Internet Gateway](../project_artifacts/screenshots/aws/internet_gateway.png) | ![NAT Gateway](../project_artifacts/screenshots/aws/nat_gateway.png) |

| VPC Route Tables Routing Topology | Network ACLs (NACL) Boundaries |
| :---: | :---: |
| ![Route Tables](../project_artifacts/screenshots/aws/routetables.png) | ![NACLs](../project_artifacts/screenshots/aws/nacls.png) |

---

## 4. State Management and Native S3 Locking with In-Context Proof

Terraform stores execution state in an Amazon S3 remote backend. Concurrency conflicts are prevented using native S3 lockfiles:

```hcl
terraform {
  required_version = ">= 1.8.0"

  backend "s3" {
    bucket       = "lumora-ecommerce-prod-tfstate-us-east-1"
    key          = "prod/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true # S3 Native Conditional Writes Locking (Terraform 1.8+)
  }
}
```

### Key Technical Advantages of S3 Native Locking:
1. **Zero External Overhead**: Eliminates the operational complexity and cost of provisioning an auxiliary DynamoDB table.
2. **Deterministic Race Prevention**: S3 enforces atomic PUT conditions; if Jenkins Build #1 is applying infrastructure, Jenkins Build #2 receives a state lock exception immediately.
3. **Data Protection**: Encryption at rest is enforced using standard AWS-managed AES-256 keys, and bucket versioning ensures recovery from accidental state corruption.

---

## 5. Security Groups and Least-Privilege Boundaries

Network traffic is strictly controlled through dedicated security groups:

| Security Group Name | Ingress Rules | Egress Rules | Purpose |
| :--- | :--- | :--- | :--- |
| `lumora-ecommerce-prod-alb-sg` | TCP 80, TCP 443 from `0.0.0.0/0` | Outbound to EKS nodes on port 5000 | Public load balancer perimeter |
| `lumora-ecommerce-prod-jenkins-sg` | TCP 8080 (UI), TCP 22 (SSH) | Full outbound internet access | Jenkins build automation controller |
| `lumora-ecommerce-prod-eks-nodes-sg` | TCP 5000 from ALB SG, intra-cluster | Outbound internet via NAT Gateway | EKS worker nodes hosting Flask pods |
| `lumora-ecommerce-prod-mongodb-sg` | TCP 27017 from EKS Nodes SG only | Outbound internal to VPC | Completely isolated MongoDB database |

| Security Groups Configuration | AWS Application Load Balancer (ALB) |
| :---: | :---: |
| ![Security Groups](../project_artifacts/screenshots/aws/security_groups.png) | ![AWS ALB](../project_artifacts/screenshots/aws/alb.png) |

---

## 6. Secrets Management and AWS Budgets with In-Context Proof

### 6.1. AWS Secrets Manager Integration (`secrets.tf`)
Passwords and signing keys are dynamically generated inside Terraform:
- `random_password.flask_secret_key`: 32-character high-entropy secret.
- `random_password.admin_password`: 16-character complex administrator password.
- `random_password.mongo_root_password`: 16-character database root credential.

These credentials are encrypted inside AWS Secrets Manager (`lumora-ecommerce-prod-secrets`). Crucially, `recovery_window_in_days = 0` is set to ensure instant resource destruction without retention charges when the capstone is torn down.

![AWS Secrets Manager Secret Console](../project_artifacts/screenshots/aws/secrets.png)

### 6.2. Shift-Left Cost Governance (`budgets.tf`)
An AWS Budgets resource actively monitors spending against a $25 USD monthly threshold:
- **Warning Alarm (80%)**: Dispatches email alerts when actual cloud spending exceeds $20.
- **Forecasted Alarm (100%)**: Fires predictive alerts if spending trends indicate month-end breach.
- **Critical Alarm (100%)**: Alerts the team immediately when cloud spend reaches $25.



---

## 7. FinOps Cost Toggles and Plan Execution Proof

In [terraform.tfvars](../terraform/terraform.tfvars), we provide conditional toggles:

```hcl
# Set to true when starting Sprint 4 (Kubernetes deployment)
# Set to false to destroy EKS and save ~$140/month when not in active use
enable_eks = false

# Set to true together with enable_eks — NAT Gateway is only needed for private EKS nodes
# Set to false to destroy NAT Gateway and save ~$33/month when EKS is not running
enable_nat_gateway = false
```

When `enable_eks = false`, Terraform calculates `count = 0` for both the EKS module and the NAT Gateway, saving ~$175/month while allowing all other VPC, Jenkins, and Ansible tests to run without financial penalties.




