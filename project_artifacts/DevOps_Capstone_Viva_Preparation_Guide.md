# Lumora E-Commerce DevOps Platform: Capstone Viva & Technical Defense Guide

This document is the master technical defense and viva preparation guide for the Lumora E-Commerce DevOps Capstone. It provides exhaustive, production-grade answers, architectural justifications, command syntax, and troubleshooting rationale covering every technical domain evaluated by the panel.

---

## Table of Contents

1. [Architecture & Platform Strategy](#1-architecture--platform-strategy)
2. [Containerization: Docker & Docker Compose](#2-containerization-docker--docker-compose)
3. [Continuous Integration & Jenkins Automation](#3-continuous-integration--jenkins-automation)
4. [Container Registry & Artifact Governance (Amazon ECR)](#4-container-registry--artifact-governance-amazon-ecr)
5. [Infrastructure as Code with Terraform & AWS VPC](#5-infrastructure-as-code-with-terraform--aws-vpc)
6. [Configuration Management with Ansible](#6-configuration-management-with-ansible)
7. [Kubernetes Orchestration & Microservices (Amazon EKS)](#7-kubernetes-orchestration--microservices-amazon-eks)
8. [Edge Networking, DNS & Cloudflare ALB Ingress](#8-edge-networking-dns--cloudflare-alb-ingress)
9. [Observability & Site Reliability Engineering (Prometheus & Grafana)](#9-observability--site-reliability-engineering-prometheus--grafana)
10. [Shift-Left Security (DevSecOps with Trivy) & FinOps Cost Governance](#10-shift-left-security-devsecops-with-trivy--finops-cost-governance)
11. [Live Viva Defense & Architectural Elevator Pitches](#11-live-viva-defense--architectural-elevator-pitches)

---

## 1. Architecture & Platform Strategy

### Q1.1: Walk me through the end-to-end flow when a developer pushes a code commit.
**Answer:**  
1. **Developer Action**: A developer pushes code or merges a PR to the `main` branch of `https://github.com/Saranyaharish93/hv-ecommerce-devops`.
2. **Webhook Trigger**: A GitHub Webhook sends an HTTP POST payload to the Jenkins Controller at `http://32.195.28.191:8080/github-webhook/`.
3. **Pipeline Orchestration**: Jenkins automatically initiates the 16-stage declarative pipeline (`hv-ecommerce-devops-pipeline`).
4. **Pre-flight & Hygiene**: Jenkins verifies CLI binaries (`terraform`, `aws`, `infracost`), validates IAM Instance Profile credentials via `aws sts get-caller-identity`, and runs `terraform fmt -check` and `terraform validate`.
5. **State Planning & FinOps**: Terraform builds the execution graph against the S3 remote state (`lumora-ecommerce-prod-tfstate-us-east-1`) using native S3 conditional write locking. Infracost analyzes `tfplan` to estimate monthly financial impact.
6. **Governance Gate**: An interactive manual approval prompt halts the pipeline on `main` before `terraform apply` executes.
7. **Quality & Security Gates**: Ansible playbook syntax is verified; Pytest runs unit tests and mock MongoDB tests; Docker BuildKit builds the container image as unprivileged `appuser`; Trivy scans the image for `HIGH` and `CRITICAL` CVEs.
8. **Artifact Promotion**: The verified container image is tagged with `${BUILD_NUMBER}` and `latest`, then pushed to Amazon ECR.
9. **Zero-Downtime Rollout (GitOps)**: If the EKS cluster is `ACTIVE`, Jenkins pushes the image to ECR, commits the immutable tag to `k8s/kustomization.yml`, and Argo CD syncs `k8s/` into `lumora-prod` (auto-sync + self-heal). The AWS Load Balancer Controller routes traffic to pod private IPs (`target-type: ip`) while Kubernetes performs a zero-downtime rolling update.

### Q1.2: Why did you implement both Terraform and Ansible instead of using just one?
**Answer:**  
Terraform and Ansible solve two fundamentally different problems in platform engineering:
- **Terraform (Infrastructure Provisioning)**: Declarative, state-driven orchestration. It manages cloud infrastructure lifecycle (VPCs, CIDR blocks, Subnets, Route Tables, Internet Gateways, NAT Gateways, EKS Clusters, IAM Roles, Security Groups). It maintains a state file tracking cloud resource IDs.
- **Ansible (Configuration Management)**: Procedural/declarative, agentless, host-level configuration. It configures the operating system inside running EC2 instances. Ansible installs packages at pinned versions (Java 21, Docker Engine, kubectl, AWS CLI, Terraform, Infracost), configures OS daemons, registers system users and groups, templates Jenkins configuration XMLs, and enforces **idempotency** (`changed=0`) across repeated runs without destroying or recreating virtual machines.

---

## 2. Containerization: Docker & Docker Compose

### Q2.1: Explain the Dockerfile design and how you optimized the container image.
**Answer:**  
Our Dockerfile implements industry container security and optimization best practices:
1. **Lightweight Base Image**: Uses `python:3.12-slim`, drastically reducing attack surface and image size compared to full Debian/Ubuntu images.
2. **Layer Caching**: `COPY requirements.txt .` and `RUN pip install --no-cache-dir -r requirements.txt` are executed *before* copying application source code. Docker caches the dependency layer; subsequent code edits rebuild in seconds without reinstalling Python packages.
3. **Non-Root Execution**: Creates a dedicated system user and group (`appuser`, UID 1000) and sets `USER appuser`. If an application-level vulnerability is exploited, the attacker cannot escalate privileges on the host kernel or access host namespaces.
4. **Build Hygiene**: A comprehensive `.dockerignore` excludes `.git`, `.terraform`, `*.tfstate`, `.env`, test mocks, and Jenkins files from entering the Docker build context.
5. **Production WSGI Server**: Uses **Gunicorn** (`gunicorn -w 2 -b 0.0.0.0:5000 run:app`) instead of Flask's built-in single-threaded development server.

### Q2.2: What is the role of Docker Compose in this project versus Kubernetes?
**Answer:**  
- **Docker Compose (`docker-compose.yml`)**: Designed for **local development and developer inner-loop testing**. It orchestrates the multi-container stack (Flask web app + MongoDB container) on a developer's workstation using a shared Docker bridge network (`lumora-network`) with service discovery by DNS name (`mongodb://mongo:27017/lumora_db`) and local volume bindings (`./data/db`).
- **Kubernetes (EKS)**: Designed for **production runtime orchestration**. It provides distributed high availability across multiple AWS Availability Zones, horizontal autoscaling (HPA), zero-downtime rolling deployments, self-healing liveness probes, automated secret injection via AWS Secrets Store CSI, and public internet routing via AWS Application Load Balancer Ingress.

---

## 3. Continuous Integration & Jenkins Automation

### Q3.1: Why did you choose a Declarative Pipeline over a Scripted Pipeline?
**Answer:**  
Declarative syntax enforces a strict, opinionated, structured hierarchy (`pipeline { agent { stages { stage { steps } } } }`):
1. **Readability & Governance**: Stage boundaries, environment blocks, and tool definitions are standardized, making pipelines easy to review across a team.
2. **Built-in Post Actions**: Native `post { always { deleteDir() } failure { ... } success { ... } }` blocks guarantee workspace hygiene and error notifications without nested try-catch blocks.
3. **Declarative Directives**: Built-in support for `when { expression { ... } }`, `options { disableConcurrentBuilds(); buildDiscarder(...) }`, and `input` approval gates without writing custom Groovy classes.

### Q3.2: How does Jenkins authenticate to AWS without storing hardcoded credentials?
**Answer:**  
Jenkins runs on an Amazon EC2 instance assigned an **IAM Instance Profile** (`lumora-ecommerce-prod-jenkins-role`).
- The controller uses **EC2 Instance Metadata Service Version 2 (IMDSv2)** to dynamically fetch session tokens and short-lived temporary security credentials.
- In Jenkins, pipeline stages execute `aws`, `terraform`, and `docker login` commands without hardcoded `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` environment variables.
- Token theft via SSRF (Server-Side Request Forgery) is mitigated because IMDSv2 enforces session-oriented HTTP `PUT` tokens with a hop limit of 1.

### Q3.3: How does the pipeline conditionally handle EKS deployment when the cluster is stopped?
**Answer:**  
To prevent CI pipeline failure during periods when the EKS cluster is scaled down to save cloud costs, Stage 16 wraps the rollout in an `expression` guard:
```groovy
when {
    expression {
        return sh(
            script: 'aws eks describe-cluster --name lumora-ecommerce-prod --region us-east-1 --query "cluster.status" --output text 2>/dev/null | grep -q "ACTIVE"',
            returnStatus: true
        ) == 0
    }
}
```
If the cluster status is not `ACTIVE`, Jenkins logs an informative skip message and completes the build with a green checkmark, having successfully tested, built, scanned, and published the container image to Amazon ECR.

---

## 4. Container Registry & Artifact Governance (Amazon ECR)

### Q4.1: How does Jenkins authenticate with Amazon ECR securely?
**Answer:**  
Jenkins utilizes the AWS CLI `get-login-password` API to retrieve an ephemeral authentication token valid for 12 hours:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 759530261212.dkr.ecr.us-east-1.amazonaws.com
```
Because the EC2 controller assumes the IAM Instance Profile, no static registry credentials exist. The token is piped directly to `docker login` via standard input, preventing credentials from leaking into process tables (`ps aux`) or Jenkins console logs.

### Q4.2: What is your container image tagging strategy and why is it important?
**Answer:**  
We employ a dual-tagging strategy:
1. **Immutable Semantic Tag**: `${BUILD_NUMBER}` (e.g., `lumora-ecommerce-flask:14`). Every build creates a unique, immutable artifact tied directly to a specific Jenkins execution and Git commit SHA. If a production regression occurs, rolling back to an exact known good build is instantaneous.
2. **Floating Reference Tag**: `latest` (e.g., `lumora-ecommerce-flask:latest`). Points to the most recently built and scanned image for human inspection and test environments.

---

## 5. Infrastructure as Code with Terraform & AWS VPC

### Q5.1: Why did you use S3 native state locking instead of DynamoDB for Terraform?
**Answer:**  
Starting in Terraform v1.8+, Amazon S3 natively supports conditional writes (`PutObject` with conditional constraints), enabling state locking directly inside S3 (`use_lockfile = true`):
- **Cost Reduction**: Eliminates the DynamoDB table provisioned solely for state locking.
- **Operational Simplicity**: Removes IAM permissions, table provisioning, and capacity management for DynamoDB.
- **Zero Race Conditions**: S3 atomic conditional writes prevent multiple engineers or concurrent Jenkins builds from applying conflicting infrastructure changes.

### Q5.2: Explain your VPC subnet sizing strategy (`/20` vs `/24`).
**Answer:**  
In our Multi-AZ AWS VPC (`10.0.0.0/16`):
- **Public Subnets (`/24`, 251 usable IPs)**: Host NAT Gateways, the Application Load Balancer, and the Jenkins Controller. These components require very few IP addresses.
- **Restricted Database Subnets (`/24`, 251 usable IPs)**: Host MongoDB StatefulSet pods with static endpoints.
- **Private Compute Subnets (`/20`, 4,091 usable IPs each in AZ-a and AZ-b)**: Under the **AWS VPC CNI plugin**, every Kubernetes pod running in EKS receives a real, routable private IP address assigned directly from the subnet. If these subnets were sized at `/24`, running multiple microservices, daemonsets, and autoscaling replicas would cause rapid **IP address exhaustion**, preventing new pods from scheduling. Sizing at `/20` guarantees over 8,000 available pod IPs across both AZs.

### Q5.3: How does Terraform protect the Jenkins Controller from accidental destruction?
**Answer:**  
In `terraform/modules/jenkins/main.tf`:
1. `lifecycle { ignore_changes = [ami] }`: Prevents Terraform from destroying and replacing the EC2 instance whenever AWS publishes a new Ubuntu 24.04 LTS AMI release.
2. `aws_eip.jenkins`: An explicit AWS Elastic IP binds the static public IP `32.195.28.191` to the instance. Even if the VM stops and restarts, the IP remains fixed, ensuring GitHub webhooks and admin access never break.

---

## 6. Configuration Management with Ansible

### Q6.1: Why did you structure Ansible into 7 modular roles?
**Answer:**  
Monolithic playbooks violate separation of concerns and reduce maintainability. We modularized configuration into 7 independent roles:
1. `common`: Base OS packages, firewall, timezone, NTP.
2. `aws_cli`: AWS CLI v2 installation and configuration.
3. `docker`: Docker Engine, BuildKit, daemon configuration, group permissions.
4. `kubectl`: Pinned Kubernetes CLI matching the EKS control plane version.
5. `terraform`: Pinned HashiCorp Terraform binary.
6. `infracost`: Infracost FinOps CLI.
7. `jenkins`: OpenJDK 21, Jenkins LTS, service automation, and initial job templating.

Each role encapsulates its own `tasks`, `vars`, `handlers`, and `templates`. If a tool version changes, engineers update only that specific role without risking regression on other system components.

### Q6.2: How do you validate Ansible idempotency?
**Answer:**  
Idempotency ensures that running a playbook repeatedly yields the exact same state without unintended side effects. We test this using a **two-pass execution**:
1. **Pass 1**: Executes the playbook against the host; tasks report `changed > 0` as software is installed and configured.
2. **Pass 2**: Immediately re-executes the exact same playbook. The recap must report **`changed=0, failed=0`**. This proves the configuration has fully converged and no configuration drift exists.

### Q6.3: How does Jenkins execute Docker builds without root privileges?
**Answer:**  
Running Jenkins as `root` is a dangerous security risk. In `roles/docker/tasks/main.yml`, our playbook ensures the `docker` UNIX group exists and appends the `jenkins` user to it:
```yaml
- name: Add jenkins user to docker group
  user:
    name: jenkins
    groups: docker
    append: yes
```
This enables the unprivileged `jenkins` process to communicate directly with the Docker daemon UNIX socket (`/var/run/docker.sock`) without requiring `sudo` privileges.

---

## 7. Kubernetes Orchestration & Microservices (Amazon EKS)

### Q7.1: What is the difference between a Kubernetes ConfigMap and a Secret?
**Answer:**  
- **ConfigMap (`k8s/02-configmap.yml`)**: Designed for non-sensitive configuration data (e.g., `PORT: "5000"`, `FLASK_ENV: "production"`, `LOG_LEVEL: "INFO"`). Stored in plaintext and exposed as environment variables or volume mounts.
- **Secret (`k8s/03-secret.yml`)**: Designed for sensitive data (database passwords, tokens, private keys). Native Kubernetes Secrets are Base64-encoded, which is **not encryption**.
- **Lumora Zero-Secret Git Standard**: To prevent storing secrets in Git, we integrate the **AWS Secrets Store CSI Driver**. Secrets are generated in Terraform and stored in AWS Secrets Manager. A `SecretProviderClass` mounts secrets directly from AWS Secrets Manager into the container filesystem at runtime, syncing them into a Kubernetes Secret in memory without committing credentials to Git.

### Q7.2: Why is MongoDB deployed as a StatefulSet while Flask is a Deployment?
**Answer:**  
- **Flask (Stateless Deployment)**: Web pods do not store persistent state. Pods can be created, destroyed, or scaled horizontally (2 to 5 pods) dynamically. If a pod terminates, any new pod with an identical image immediately handles web traffic.
- **MongoDB (StatefulSet `k8s/04-mongo.yml`)**: Database workloads require data durability and predictable identity:
  1. **Stable Network Identity**: Pods receive ordered, deterministic DNS names (`mongodb-0.mongo-service`).
  2. **Dedicated Storage Binding**: Uses `volumeClaimTemplates` to provision dedicated Amazon EBS `gp3` volumes. When `mongodb-0` restarts or reschedules on another node, Kubernetes reattaches the exact same EBS volume, preventing data loss or split-brain corruption.
  3. **Ordered Rollouts**: StatefulSets scale and update in strict sequential order (0, then 1, etc.).

### Q7.3: Explain the decoupling of Liveness and Readiness Probes.
**Answer:**  
Coupling liveness directly to backing dependencies like a database is a major architectural anti-pattern:
- **Liveness Probe (`/health` or `/health/live`)**: Checks if the Python/Gunicorn web process is running. If this probe fails repeatedly, kubelet **kills and restarts the container**.
- **Readiness Probe (`/health/ready`)**: Actively tests database connectivity by querying MongoDB. If MongoDB experiences temporary latency or connection pool exhaustion, the readiness probe fails. Kubernetes **temporarily removes the pod from ALB service endpoints**, stopping new requests from reaching it.
- **Why Decouple?**: If database latency triggered the *liveness* probe, Kubernetes would restart healthy web pods in an endless restart loop (cascading failure), taking down the entire cluster.

### Q7.4: How does the Horizontal Pod Autoscaler (HPA) scale the application?
**Answer:**  
In `k8s/06-hpa.yml`, the HPA v2 controller queries the **Kubernetes Metrics Server** every 15 seconds to monitor pod resource consumption:
- **Scaling Target**: Minimum 2 pods, maximum 5 pods.
- **Metric Thresholds**: Target average CPU utilization of **70%** and target average Memory utilization of **80%**.
- **Scaling Formula**:  
  $$\text{Desired Replicas} = \lceil \text{Current Replicas} \times \frac{\text{Current Metric Value}}{\text{Target Metric Value}} \rceil$$
- **Stabilization Window**: Default scale-down stabilization window (300 seconds) prevents "flapping" (rapid oscillations of adding and removing pods during bursty traffic).

---

## 8. Edge Networking, DNS & Cloudflare ALB Ingress

### Q8.1: Why did Cloudflare timeout initially when proxying traffic to the AWS ALB, and how was it solved?
**Answer:**  
- **Root Cause**: The Kubernetes Ingress (`k8s/05-service-ingress.yml`) configured the ALB to listen on HTTP (port 80):
  `alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}]'`
  By default, Cloudflare Proxy (orange cloud) uses **"Full"** or **"Full (strict)"** SSL/TLS encryption. In Full mode, when a user visits `https://lumora.thiagarajanb.dpdns.org`, Cloudflare terminates the client TLS connection and attempts to connect to the origin (the AWS ALB) over **HTTPS (port 443)**. Because the ALB had no listener on port 443, Cloudflare's TCP/TLS connection timed out after 15 seconds, returning **Cloudflare Error 522**.
- **Solution**: Set Cloudflare SSL/TLS mode to **"Flexible"**:
  - **Browser ↔ Cloudflare**: Fully encrypted over HTTPS (port 443) using Cloudflare's edge certificate.
  - **Cloudflare ↔ AWS ALB**: Plain HTTP (port 80).
  - We also enabled **"Always Use HTTPS"** on Cloudflare to redirect `http://` requests to `https://` without redirect loops, since the origin ALB does not force HTTPS redirects.

### Q8.2: Why is `target-type: ip` used instead of `target-type: instance` on the ALB Ingress?
**Answer:**  
- **`target-type: instance` (NodePort routing)**: Traffic from the ALB travels to a worker node's NodePort on port 30000+, where `kube-proxy` iptables rules route it across the cluster to the actual pod IP. This introduces an extra network hop, increases packet latency, and can mask the client's true IP.
- **`target-type: ip` (Direct pod routing)**: The AWS Load Balancer Controller registers the pod's native VPC private IP address directly into the ALB Target Group. The ALB routes traffic directly to the container in a single network hop, bypassing `kube-proxy` and improving throughput.

---

## 9. Observability & Site Reliability Engineering (Prometheus & Grafana)

### Q9.1: What is the difference between Metrics Server and Prometheus in Kubernetes?
**Answer:**  
- **Metrics Server**: A lightweight, in-memory, short-term metrics aggregator. It scrapes resource metrics (`container_cpu_usage_seconds_total`, `container_memory_working_set_bytes`) from kubelet Summary APIs on each node. It does **not** store historical data or support alerting; its sole purpose is providing live metrics for `kubectl top` and driving Horizontal Pod Autoscaling (HPA).
- **Prometheus**: A comprehensive Time Series Database (TSDB) and monitoring platform. It provides long-term metrics storage, multidimensional data modeling with key-value labels, PromQL query language, alerting rules evaluated via Alertmanager, and rich dashboard visualizations in Grafana.

### Q9.2: What are the "Four Golden Signals" of SRE and how are they monitored?
**Answer:**  
1. **Latency**: The time taken to service a request. Tracked using Flask request duration histograms (`flask_http_request_duration_seconds_bucket`) in Grafana, plotting P50, P95, and P99 percentiles.
2. **Traffic**: Demand placed on the system. Tracked via requests per second (RPS): `rate(flask_http_request_total[5m])`.
3. **Errors**: The rate of requests that fail. Monitored via HTTP 4xx and 5xx status codes: `rate(flask_http_request_total{status=~"5.."}[5m])`.
4. **Saturation**: How full the service is. Monitored via EC2 node CPU/memory load (`node_cpu_seconds_total`), container memory limits, and EBS disk I/O metrics.

---

## 10. Shift-Left Security (DevSecOps with Trivy) & FinOps Cost Governance

### Q10.1: How is Shift-Left Security (DevSecOps) implemented across the lifecycle?
**Answer:**  
Shift-Left Security means catching security risks at the earliest possible stage:
1. **Commit Phase**: `.dockerignore` prevents accidental leakage of SSH private keys, `.env` files, or local `.tfstate` files into Docker build contexts.
2. **Build Phase**: Dockerfile enforces non-root execution (`appuser`, UID 1000) and layer minimization.
3. **CI Phase (Static Analysis & Vulnerability Scanning)**:
   - Jenkins runs **Trivy** to scan OS packages and application dependencies for known CVEs:
     ```bash
     trivy image --severity HIGH,CRITICAL --exit-code 0 --format table lumora-ecommerce-flask:${IMAGE_TAG}
     ```
   - In production governance, `--exit-code 1` halts the pipeline if unfixed Critical vulnerabilities are found.
4. **Deploy Phase (Runtime Protection)**:
   - Zero hardcoded credentials in Git. Credentials injected dynamically via AWS Secrets Store CSI.
   - Least-privilege AWS IAM roles assigned to EC2 controllers and EKS nodes via Instance Profiles.

### Q10.2: Compare Infracost (Shift-Left FinOps) and AWS Budgets.
**Answer:**  
- **Infracost (Shift-Left / Proactive)**: Runs during the CI stage *before* any infrastructure is created. It parses the Terraform execution plan (`tfplan`) and queries cloud pricing APIs to calculate the projected monthly dollar increase/decrease. It allows engineers and evaluators to catch expensive architecture oversights during pull request review.
- **AWS Budgets (Reactive / Governance)**: Tracks actual and forecasted cloud spending against a fixed budget ($25/month). It evaluates actual AWS Cost and Usage data and sends email notifications when actual spend exceeds 80% ($20) or 100% ($25).

### Q10.3: What specific cost optimization levers did you implement in this project?
**Answer:**  
1. **Infrastructure Cost Toggles**: In `terraform.tfvars`, setting `enable_eks = false` and `enable_nat_gateway = false` spins down the EKS cluster and dual NAT Gateways when live testing is inactive, saving **~$175/month**.
2. **Right-Sizing Compute**: Utilizing `t3.small` (2 vCPU, 2 GiB RAM) instances with burstable CPU credits for the Jenkins controller and EKS nodes rather than expensive general-purpose instances (`m5.large`).
3. **Immediate Secret Deletion**: AWS Secrets Manager configured with `recovery_window_in_days = 0` to eliminate holding costs upon teardown.
4. **Automated Elastic Autoscaling**: HPA scales pods down to 2 replicas during low traffic, avoiding resource over-provisioning.
5. **S3 Native State Locking**: Eliminates auxiliary DynamoDB read/write unit costs.

---

## 11. Live Viva Defense & Architectural Elevator Pitches

### 1-Minute Architectural Summary (For the Panel):
> *"Lumora is a production-grade full-stack e-commerce platform built with Python Flask and MongoDB. To deliver enterprise resilience and operational excellence, we implemented a complete DevOps lifecycle:*
> *All cloud infrastructure is codified in modular **Terraform** on AWS across a Multi-AZ VPC with public, private, and database subnets, utilizing S3 native conditional write state locking.*
> *The Jenkins controller is provisioned via Terraform and hardened via **Ansible** using 7 modular roles enforcing idempotency.*
> *Our 16-stage **Declarative Jenkins Pipeline** executes automated Pytest validation, non-root Docker builds, **Trivy** vulnerability scanning, and pushes immutable semantically tagged images to **Amazon ECR**.*
> *Workloads are orchestrated on **Amazon EKS** featuring decoupled Liveness/Readiness probes, MongoDB StatefulSets with EBS gp3 persistence, automated scaling via **HPA v2**, and **AWS Secrets Store CSI** out-of-band secret injection.*
> *Finally, public traffic routes via **Cloudflare DNS** and an **AWS Application Load Balancer Ingress**, with comprehensive FinOps cost governance managed through **Infracost** and **AWS Budgets**."*
