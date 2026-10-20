# Lumora E-Commerce DevOps Platform: Capstone Viva & Technical Defense Guide

This document is an internal preparation guide for all project team members. It consolidates the most critical technical questions, architectural trade-offs, and defense rationale likely to be asked by evaluators during the Capstone Viva examination.

---

## Table of Contents

1. [Architecture & Platform Strategy](#1-architecture--platform-strategy)
2. [CI/CD & Jenkins Automation](#2-cicd--jenkins-automation)
3. [Infrastructure as Code with Terraform](#3-infrastructure-as-code-with-terraform)
4. [Configuration Management with Ansible](#4-configuration-management-with-ansible)
5. [Kubernetes Orchestration & Microservices (EKS)](#5-kubernetes-orchestration--microservices-eks)
6. [Observability & Reliability Engineering (SRE)](#6-observability--reliability-engineering-sre)
7. [Shift-Left Security (DevSecOps) & FinOps Governance](#7-shift-left-security-devsecops--finops-governance)

---

## 1. Architecture & Platform Strategy

### Q1.1: Walk me through the end-to-end flow when a developer pushes a code commit.
**Answer:**  
1. The developer pushes code to a feature branch on GitHub and submits a Pull Request to `main`.
2. A GitHub Webhook fires an HTTP POST payload to the Jenkins Controller (`32.195.28.191:8080/github-webhook/`).
3. Jenkins triggers the 16-stage declarative pipeline (`hv-ecommerce-devops-pipeline`).
4. Prerequisites (Terraform, AWS CLI, IAM identity) are verified.
5. Terraform formats, validates, and plans infrastructure changes against the S3 remote state.
6. Infracost analyzes the plan to estimate monthly cloud cost differences.
7. On the `main` branch, an approval gate prompts the operator before running `terraform apply`.
8. Ansible syntax is verified.
9. Pytest executes unit tests and database mock tests.
10. Docker BuildKit builds the container image as non-root `appuser`.
11. Trivy scans the image for High and Critical vulnerabilities.
12. The immutable image is tagged (`${BUILD_NUMBER}` and `latest`) and pushed to Amazon ECR.
13. If EKS is active, `setup_metrics_server.sh` verifies cluster prerequisites, and `kubectl apply -k k8s/` performs a zero-downtime rolling update on the Flask deployment.

### Q1.2: Why did you implement both Terraform and Ansible instead of just one?
**Answer:**  
Terraform and Ansible have fundamentally different core strengths:
- **Terraform** is declarative orchestration built for infrastructure lifecycle management (VPCs, subnets, EKS clusters, IAM roles, Security Groups).
- **Ansible** is purpose-built for configuration management inside running operating systems. It ensures packages (Docker, kubectl, AWS CLI, Java 21) are installed at exact versions, manages configuration templates, and guarantees **idempotency** (`changed=0`) across repeated runs without altering the underlying cloud infrastructure.

---

## 2. CI/CD & Jenkins Automation

### Q2.1: Why did you choose a Declarative Pipeline over a Scripted Pipeline?
**Answer:**  
Declarative syntax enforces an opinionated structure: clear stage boundaries, built-in environment blocks, structured post-actions (`always`, `success`, `failure`), and native conditional execution (`when`). It separates pipeline flow from Groovy scripting, making the pipeline easier to read, audit, and maintain across team members.

### Q2.2: How does Jenkins authenticate to AWS securely?
**Answer:**  
The Jenkins EC2 instance is attached to an IAM Instance Profile (`lumora-ecommerce-prod-jenkins-role`). Jenkins automatically retrieves short-lived temporary security credentials from the EC2 Instance Metadata Service (IMDSv2). No long-lived `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` credentials are hardcoded in Git or Jenkins credentials.

### Q2.3: Why is the EKS deployment stage guarded with an `expression` block?
**Answer:**  
To prevent CI pipeline failures when the EKS cluster is deliberately spun down to save cloud costs. The pipeline runs an AWS CLI check (`aws eks describe-cluster ... | grep -q "ACTIVE"`). If the cluster is not provisioned, the pipeline completes all prior CI stages (lint, plan, test, build, scan, push to ECR) and skips Kubernetes rollout cleanly.

---

## 3. Infrastructure as Code with Terraform

### Q3.1: Why did you use S3 native locking instead of DynamoDB for Terraform?
**Answer:**  
Starting in Terraform v1.8+, AWS S3 supports native conditional writes, allowing state locking directly via S3 (`use_lockfile = true`). This eliminates the operational overhead and cost of provisioning an auxiliary DynamoDB table, avoids cold-start locking delays, and guarantees race condition prevention during concurrent CI runs.

### Q3.2: Why are private compute subnets sized at `/20` while public and restricted subnets are `/24`?
**Answer:**  
Public subnets only host load balancers, NAT Gateways, and the Jenkins controller, requiring fewer than 30 IPs. Restricted subnets host database StatefulSets with minimal static IPs. However, private compute subnets host EKS worker nodes. Under the AWS VPC CNI plugin, every Kubernetes pod receives its own private IP address directly from the subnet. Sizing compute subnets at `/20` provides 4,091 IP addresses per AZ, preventing IP exhaustion during high pod autoscaling events.

### Q3.3: What prevents `terraform apply` from recreating the Jenkins EC2 server and changing its IP?
**Answer:**  
Two critical controls protect the controller:
1. `lifecycle { ignore_changes = [ami] }` in `modules/jenkins/main.tf` ensures Canonical base AMI updates do not trigger instance recreation.
2. An explicit `aws_eip.jenkins` resource permanently binds the static public IP `32.195.28.191` to the instance.

---

## 4. Configuration Management with Ansible

### Q4.1: Why did you separate Jenkins setup into 7 modular roles?
**Answer:**  
Monolithic playbooks violate separation of concerns. Modular roles (`common`, `aws_cli`, `docker`, `kubectl`, `terraform`, `infracost`, `jenkins`) isolate variables, handlers, and tasks. If a tool version changes (e.g., upgrading kubectl), only `roles/kubectl/tasks/main.yml` is updated without touching the Jenkins or Docker configurations.

### Q4.2: How do you validate Ansible idempotency?
**Answer:**  
We execute a two-pass test against the controller:
1. First pass applies packages and configurations (`changed > 0`).
2. Second pass re-evaluates system state and must output `changed=0, failed=0` in the play recap. This proves the system has fully converged and is free of drift.

### Q4.3: How does Jenkins build Docker containers without running as root?
**Answer:**  
Running Jenkins as `root` is a dangerous security risk. In `roles/docker/tasks/main.yml`, our playbook ensures the `docker` UNIX group exists and appends the `jenkins` user to it (`usermod -aG docker jenkins`). This allows the unprivileged Jenkins user to interact with the Docker daemon UNIX socket (`/var/run/docker.sock`).

---

## 5. Kubernetes Orchestration & Microservices (EKS)

### Q5.1: Why did you deploy MongoDB as a StatefulSet instead of a Deployment?
**Answer:**  
Databases require stable network identities and persistent state:
1. Pods have stable, predictable network hostnames (`mongodb-0`).
2. Pods start and terminate in strict sequential order.
3. Dedicated `volumeClaimTemplates` guarantee that pod replicas re-attach to their exact Amazon EBS `gp3` volumes upon restarts, avoiding data corruption.

### Q5.2: Why are Liveness and Readiness probes pointing to different endpoints?
**Answer:**  
Coupling liveness directly to database connectivity is an anti-pattern:
- `/health` and `/health/live` check whether the Python/Gunicorn web process is running (Liveness).
- `/health/ready` actively pings MongoDB (Readiness).
If MongoDB experiences transient latency, the pod fails readiness and the ALB stops routing traffic to it. The pod is NOT restarted. If it were coupled to liveness, Kubernetes would kill and restart healthy web containers, creating a cascading failure loop.

### Q5.3: How does the zero-secret Git policy work in Kubernetes?
**Answer:**  
We use the **AWS Secrets Store CSI Driver**. Passwords are generated in Terraform and stored in AWS Secrets Manager. A `SecretProviderClass` references the secret. The CSI driver uses the EKS node IAM role to retrieve the credentials out-of-band and mounts them into `/mnt/secrets-store`, simultaneously syncing them into a Kubernetes Opaque Secret in memory. Zero credentials are committed to Git.

### Q5.4: Why is `target-type: ip` used in the ALB Ingress annotation?
**Answer:**  
With `target-type: instance`, traffic goes to a node's NodePort and uses `kube-proxy` iptables routing, adding network hops and losing client IP visibility. With `target-type: ip`, the AWS Load Balancer Controller registers the pod's native VPC private IP directly into the ALB Target Group, enabling direct one-hop traffic routing.

---

## 6. Observability & Reliability Engineering (SRE)

### Q6.1: What is the difference between Metrics Server and Prometheus in Kubernetes?
**Answer:**  
Metrics Server is an in-memory, short-term metrics aggregator designed solely for Kubernetes core orchestration (HPA and `kubectl top`). It does not store historical data. Prometheus is a full-featured time-series database (TSDB) with long-term retention, PromQL query language, alerting rules (Alertmanager), and rich visual dashboarding integrations via Grafana.

### Q6.2: What are the Four Golden Signals and how are they monitored?
**Answer:**  
1. **Latency**: Flask HTTP request duration percentiles (P50, P95, P99) monitored in Grafana.
2. **Traffic**: Requests per second (RPS) tracked across endpoints.
3. **Errors**: 4xx and 5xx HTTP response codes measured via Prometheus counter metrics.
4. **Saturation**: EKS worker node CPU/memory load and EBS disk utilization.

---

## 7. Shift-Left Security (DevSecOps) & FinOps Governance

### Q7.1: What is Shift-Left Security and where is it applied?
**Answer:**  
Shift-Left Security means enforcing security checks as early as possible in the development lifecycle:
1. **Commit Phase**: `.dockerignore` blocks private keys, Terraform state, and logs from entering image contexts.
2. **Build Phase**: Dockerfile enforces non-root execution (`appuser`, UID 1000).
3. **CI Phase**: Trivy scans images for CVE vulnerabilities in Jenkins.
4. **Deploy Phase**: Secrets are fetched out-of-band via AWS Secrets Store CSI.

### Q7.2: What is the difference between Infracost and AWS Budgets?
**Answer:**  
- **AWS Budgets** is reactive/monitoring; it tracks actual and forecasted spend after cloud resources are created.
- **Infracost** is proactive/shift-left; it parses Terraform execution plans during the CI pull request phase, forecasting monthly cost differences *before* resources are provisioned on AWS.

### Q7.3: How does your team achieve AWS cost optimization in this project?
**Answer:**  
1. **Infracost Scanning**: Monthly cost estimation on every pull request.
2. **Modular Cost Toggles**: Setting `enable_eks = false` and `enable_nat_gateway = false` in `terraform.tfvars` saves ~$175/month during development.
3. **AWS Budgets**: $25/month ceiling with email alerts at 80% and 100% thresholds.
4. **0-Day Secret Recovery**: AWS Secrets Manager configured with `recovery_window_in_days = 0` for instant zero-holding-cost cleanup.
5. **Right-Sizing**: Using `t3.small` instances and dynamic HPA scaling (2 to 5 pods).
