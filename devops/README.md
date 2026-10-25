# Lumora E-Commerce DevOps Platform

## Master DevOps Architecture, Principles, and Platform Engineering Guide

This repository hosts the source code, Infrastructure as Code, configuration playbooks, Kubernetes manifests, and CI/CD pipelines for Lumora, a production-grade full-stack e-commerce application built on Python Flask and MongoDB.

This master documentation is designed as the primary technical reference for platform engineering, architectural evaluation, and operational procedures implemented throughout this capstone project.

---

## Table of Contents

1. [Technical and DevOps Components](#1-technical-and-devops-components)
2. [DevOps Principles Implemented](#2-devops-principles-implemented)
3. [End-to-End System Architecture with Visual Proofs](#3-end-to-end-system-architecture-with-visual-proofs)
4. [CI/CD Workflow and Pipeline Stages with In-Context Proofs](#4-cicd-workflow-and-pipeline-stages-with-in-context-proofs)
5. [Component Deep-Dive Documentation Links](#5-component-deep-dive-documentation-links)

---

## 1. Technical and DevOps Components

The platform integrates industry-standard tools across every phase of the software delivery lifecycle:

| Lifecycle Phase | Tool / Technology | Version / Specification | Technical Role in Lumora Platform |
| :--- | :--- | :--- | :--- |
| **Application Runtime** | Python / Flask | 3.12 / Flask 3.1.1 | Core RESTful web framework, templating, session state, and business logic |
| **Database Workload** | MongoDB | 7.0 Community | Document database storing product catalogs, user accounts, and transactions |
| **Web Server Gateway** | Gunicorn | 23.0.0 (2 Workers) | Production WSGI HTTP server binding port 5000 |
| **Container Engine** | Docker & Docker BuildKit | 26.x Engine / containerd | Multi-stage image build, non-root user execution (`appuser`), layer caching |
| **Container Registry** | Amazon ECR | Private Registry | Stores immutable, semantically tagged container images (`lumora-ecommerce-flask`) |
| **Infrastructure as Code** | HashiCorp Terraform | 1.8+ | Declarative multi-module infrastructure provisioning on AWS |
| **Remote State Backend** | AWS S3 + S3 Lockfile | AES-256 encrypted | Persistent remote state storage with native concurrency lock prevention |
| **Configuration Mgmt** | Ansible | 2.16+ Core | Idempotent host configuration, dependency installation, and tool bootstrapping |
| **CI/CD Orchestrator** | Jenkins LTS | 2.452+ (AWS EC2) | Declarative 16-stage pipeline orchestrating test, scan, build, IaC, and deployment |
| **Container Orchestration**| Amazon EKS | Kubernetes v1.36 | Managed Kubernetes control plane and multi-AZ EC2 worker node groups |
| **Ingress & Networking** | AWS ALB Ingress Controller | AWS Load Balancer Controller | Internet-facing application load balancing, TLS termination, and pod routing |
| **Auto-scaling** | Kubernetes HPA | HorizontalPodAutoscaler v2 | Dynamic pod scaling (2 to 5 replicas) based on CPU (70%) and Memory (80%) |
| **Secrets Management** | AWS Secrets Manager + CSI | Secrets Store CSI Driver | Out-of-band secret retrieval; zero credentials committed to source control |
| **Security Scanning** | Trivy | High/Critical Severity | Automated static analysis and image vulnerability scanning in CI pipeline |
| **Shift-Left FinOps** | Infracost CLI | Non-blocking Breakdown | Automated infrastructure monthly cost estimation during `terraform plan` |
| **Cost Governance** | AWS Budgets | $25/month threshold alarms| Real-time spend tracking with multi-tier email alerts at 80% and 100% |
| **Observability & Monitoring**| Prometheus & Grafana | kube-prometheus-stack | Cluster metrics scraping, resource saturation monitoring, and KPI dashboards |

---

## 2. DevOps Principles Implemented

The architecture adheres strictly to core DevOps and Site Reliability Engineering (SRE) paradigms:

### 2.1. Maximum Automation with Minimal Human Intervention
Every operational step—from dependency verification, infrastructure linting, security scanning, container packaging, to artifact promotion—is codified. Manual steps are restricted exclusively to a single governance gate: approval of production infrastructure modifications on the `main` branch.

### 2.2. Infrastructure as Code (IaC) and Reproducibility
No cloud resources are provisioned manually via the AWS Management Console. All networks, subnets, route tables, security boundaries, compute instances, storage volumes, and IAM roles are expressed as modular, parameterized Terraform configurations under version control.

### 2.3. Idempotent Configuration Management
Ansible playbooks are designed so that running them once or one hundred times yields the exact same desired system state without side effects, redundant service restarts, or configuration drift.

### 2.4. Shift-Left Security (DevSecOps)
Security is integrated at the earliest stages of the commit lifecycle:
- Docker builds enforce non-root privilege execution.
- `.dockerignore` strictly isolates infrastructure code, SSH keys, logs, and artifacts from entering container images.
- Trivy performs static vulnerability scans on built images before they can be pushed to Amazon ECR.
- Sensitive passwords and tokens are never embedded into Git repositories or Kubernetes YAML manifests; they are dynamically injected via the AWS Secrets Store CSI Driver.

### 2.5. Shift-Left FinOps (Cost Transparency and Governance)
Cloud cost visibility is integrated into the developer workflow. Infracost evaluates every Terraform plan against AWS pricing APIs to forecast monthly financial deltas. In addition, an AWS Budget alarm enforces a strict $25/month project limit, and modular cost toggles (`enable_eks = false`, `enable_nat_gateway = false`) allow spinning down heavy cloud compute when not actively executing live workload tests.

### 2.6. Immutability and Semantic Tagging
Container images are immutable. Once built, tested, and scanned, the exact same container artifact is promoted through environments. Every image is tagged with both the unique Jenkins build number and the Git commit SHA.

### 2.7. Decoupled Reliability and Self-Healing
Kubernetes health monitoring decouples liveness from readiness:
- The `/health` and `/health/live` endpoint verifies the responsiveness of the web process itself.
- The `/health/ready` endpoint verifies backing database connectivity.
If MongoDB experiences transient latency, the pod is gracefully detached from traffic routing without triggering destructive container restarts.

---

## 3. End-to-End System Architecture with Visual Proofs

The complete production cloud architecture, multi-AZ network layout, container workloads, and GitOps CI/CD flow are shown below:

*Direct Artifact Reference: [`project_artifacts/Lumora_E-Commerce_Architecture_v3.png`](../project_artifacts/Lumora_E-Commerce_Architecture_v3.png)*

![Lumora E-Commerce DevOps Platform Architecture](../project_artifacts/Lumora_E-Commerce_Architecture_v3.png)

### Visual Implementation Evidence

#### 1. AWS VPC Multi-AZ Subnets & Route Tables
![AWS VPC Subnets Console](../project_artifacts/screenshots/terraform/01_vpc_subnets.png)

#### 2. Kubernetes Workloads Running in `lumora-prod` Namespace
![Kubernetes Workloads Running](../project_artifacts/screenshots/kubernetes/02_kubectl_get_all.png)

#### 3. Live Storefront Loaded via Ingress ALB & Cloudflare
![Lumora Storefront Live](../project_artifacts/screenshots/storefront/E-commerce_portal_DNS_mapped-1.png)

#### 4. Live Back-Office Administrative & Financial Control Center
![Lumora Admin Dashboard](../project_artifacts/screenshots/storefront/E-commerce_admin_homepage.png)

---

## 4. CI/CD Workflow and Pipeline Stages with In-Context Proofs

The Jenkins Declarative Pipeline ([Jenkinsfile](file:///d:/HeroVired/Capstone/Saro/hv-ecommerce-devops/Jenkinsfile)) executes 16 structured stages upon every code push:

```
Stage 1: Checkout SCM
  └── Pulls latest commit from GitHub repository via GitSCM.

Stage 2: Validate Prerequisites
  └── Verifies presence of Terraform, AWS CLI, and active AWS IAM session identity.

Stage 3: Terraform Init
  └── Initializes remote S3 state backend with native concurrency locking.

Stage 4: Terraform Format Check
  └── Validates canonical HCL syntax using `terraform fmt -check -recursive`.

Stage 5: Terraform Validate
  └── Verifies semantic validity of modules, variables, and resource schemas.

Stage 6: Terraform Plan
  └── Synthesizes execution graph and writes binary plan file `tfplan`.

Stage 7: Archive Terraform Plan
  └── Persists `tfplan.txt` as a Jenkins fingerprint artifact for governance review.

Stage 8: FinOps Cost Estimation (Infracost)
  └── Evaluates infrastructure cost impact and archives breakdown table.

Stage 9: Terraform Apply Approval Gate
  └── Halts pipeline on `main` branch awaiting authorized engineering review.

Stage 10: Terraform Apply
  └── Applies approved infrastructure modifications idempotently to AWS.

Stage 11: Ansible Configuration Check
  └── Validates syntax of Ansible playbooks against local inventories.

Stage 12: Application Test (Pytest)
  └── Runs unit tests, endpoint validation, and mock MongoDB database tests.

Stage 13: Docker Build
  └── Packages container image using BuildKit with non-root security standards.

Stage 14: Trivy Container Security Scan
  └── Inspects image layers for CVE vulnerabilities across operating system and libraries.

Stage 15: Push Docker Image to AWS ECR
  └── Authenticates Docker to AWS ECR registry and pushes unique build and latest tags.

Stage 16: Deploy to EKS & Setup Metrics Server (Conditional Guard)
  └── If EKS is ACTIVE: boots Metrics Server, Secrets CSI, and applies manifests via Kustomize.
```

### Visual CI/CD & Security Evidence

#### 4. Jenkins 16-Stage Declarative Pipeline Run
![Jenkins 16-Stage Pipeline Success](../project_artifacts/screenshots/jenkins/02_pipeline_stage_view_success.png)

#### 5. Infracost Shift-Left Financial Breakdown Report
![Infracost Cost Breakdown Report](../project_artifacts/screenshots/security_finops/01_infracost_report_jenkins.png)

#### 6. Trivy Container Vulnerability Scan Console Output
![Trivy Scan Console Output](../project_artifacts/screenshots/jenkins/04_trivy_scan_console.png)

---

## 5. Component Deep-Dive Documentation Links

For comprehensive technical specifications, implementation details, and role-specific configurations, consult the individual component guides:

- [Jenkins CI/CD Pipeline & Controller Architecture](file:///d:/HeroVired/Capstone/Saro/hv-ecommerce-devops/devops/jenkins.md)
- [Terraform Infrastructure as Code & AWS Network Topology](file:///d:/HeroVired/Capstone/Saro/hv-ecommerce-devops/devops/terraform.md)
- [Ansible Configuration Management & Modular Playbooks](file:///d:/HeroVired/Capstone/Saro/hv-ecommerce-devops/devops/ansible.md)
- [Kubernetes Workloads, EKS Orchestration & CSI Secrets](file:///d:/HeroVired/Capstone/Saro/hv-ecommerce-devops/devops/kubernetes.md)
- [Observability, Prometheus, Grafana & Metrics Server](file:///d:/HeroVired/Capstone/Saro/hv-ecommerce-devops/devops/monitoring.md)
- [Shift-Left Security (DevSecOps) & FinOps Cost Governance](file:///d:/HeroVired/Capstone/Saro/hv-ecommerce-devops/devops/security-and-finops.md)
