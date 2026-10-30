# Terraform Infrastructure as Code (IaC)

This directory contains modular HashiCorp Terraform configurations used to provision and govern all AWS cloud infrastructure for the Lumora E-Commerce platform.

> **Deep-Dive Technical Guide**: For complete architectural specifications, network diagrams, security groups, and state management details, see the [Terraform Platform Guide](../devops/terraform.md) and [DevOps Platform Master Guide](../devops/README.md).

---

## Directory Structure

```
terraform/
├── main.tf                    # Root module: orchestrates VPC, ECR, Jenkins, EKS, and Bastion
├── variables.tf               # Root input variables and default specifications
├── outputs.tf                 # Key infrastructure outputs (VPC IDs, EIPs, ECR URLs, EKS endpoints)
├── providers.tf               # AWS provider configuration and required versions
├── versions.tf                # Minimum Terraform version constraints (>= 1.8.0)
├── secrets.tf                 # AWS Secrets Manager dynamic secret generation
├── budgets.tf                 # AWS Budgets configuration ($25/month threshold alerts)
├── terraform.tfvars           # Environment variable assignments and FinOps cost toggles
│
├── modules/
│   ├── vpc/                   # Multi-AZ VPC, subnets, route tables, IGW, and NAT Gateways
│   ├── security_groups/       # Zero-trust network segmentation and least-privilege security groups
│   ├── ecr/                   # Amazon ECR container repository with immutable image tagging
│   ├── jenkins/               # EC2 controller host, IAM role, SSM access, and Ansible inventory generator
│   └── eks/                   # Managed Kubernetes control plane, worker node groups, and IAM access entries
│
└── scripts/                   # Helper provisioning and validation scripts
```

---

## Core Engineering Features

1. **Modular Architecture**: Reusable, isolated modules for network, compute, container registry, security boundaries, and Kubernetes orchestration.
2. **S3 Remote State with Native Concurrency Locking**: State is stored in an encrypted AWS S3 bucket (`use_lockfile = true`) using native S3 conditional writes.
3. **FinOps Cost Toggles**: Configurable switches in `terraform.tfvars`:
   - `enable_eks = false` (pauses cluster outside evaluation sessions to prevent idle charges)
   - `enable_nat_gateway = false` (pauses NAT Gateways when workloads are idle)
4. **Automated Secrets Generation**: Generates 32-character cryptographically secure passwords stored directly in AWS Secrets Manager with zero plaintext in Git.
5. **SSM & Zero-Ingress Security**: Jenkins controller uses AWS Systems Manager (SSM) for management with no public inbound ports (ports 22 and 8080 closed to 0.0.0.0/0).

---

## Usage Instructions

```bash
# 1. Initialize Terraform and remote backend
terraform init

# 2. Validate HCL syntax and configuration
terraform fmt -check -recursive
terraform validate

# 3. Generate execution plan
terraform plan -out=tfplan

# 4. Apply changes (requires authorization on main branch)
terraform apply tfplan
```

---

## Related Documentation
- [Terraform Infrastructure Deep-Dive Guide](../devops/terraform.md)
- [Shift-Left Security & FinOps Governance](../devops/security-and-finops.md)
- [DevOps Platform Architecture Guide](../devops/README.md)

