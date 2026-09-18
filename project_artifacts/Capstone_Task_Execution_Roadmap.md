# 🗺️ End-to-End DevOps Capstone: Task Dependency & Execution Roadmap

> **Project Title**: Lumora E-Commerce DevOps Platform (Hero Vired Batch 16A)  
> **Repository**: `Saranyaharish93/hv-ecommerce-devops`  
> **GitHub Project Board**: [HV E-Commerce DevOps Capstone - Batch 16A](https://github.com/users/Saranyaharish93/projects/1)  
> **AWS Account**: `759530261212` | **Region**: `us-east-1`  

---

## 📌 Executive Summary & Current Project State

The project spans **6 Sprints** and **61 Issues / Tasks**. This document serves as the single source of truth for:
1. **Current completion status** across all sprints.
2. **Strict task dependencies** (what cannot start before another task finishes).
3. **Recommended chronological execution order** for the team to prevent bottlenecks and redundant work.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                CURRENT SPRINT PROGRESS                                 │
├─────────────────────────┬─────────────────────────┬────────────────────────────────────┤
│ Sprint 1: 100% COMPLETE │ Sprint 2: 80% COMPLETE  │ Sprint 3: 40% CODE / 0% EXECUTION  │
│  • #1, #2, #3, #7, #8,  │  • #4, #14: DONE        │  • Automation roles written        │
│    #9, #10, #11 [DONE]  │  • #5, #6, #15: IN REV  │  • Live execution & ping [PENDING] │
│                         │  • #12, #13: IACOFF     │                                    │
├─────────────────────────┼─────────────────────────┼────────────────────────────────────┤
│ Sprint 4: 0% COMPLETE   │ Sprint 5: 0% COMPLETE   │ Sprint 6: 15% COMPLETE             │
│  • K8s manifests & CI   │  • Prometheus & Grafana │  • #57 Diagram: DONE               │
│  • Blocked on S2/S3/EKS │  • Blocked on Sprint 4  │  • Final validation: PENDING       │
└─────────────────────────┴─────────────────────────┴────────────────────────────────────┘
```

---

## 🌳 Master Dependency Tree & Critical Path

The diagram below outlines the core critical path of the entire project lifecycle. Tasks must flow left-to-right along the arrows.

```mermaid
flowchart TD
    subgraph S1["Sprint 1: Architecture & Base VPC"]
        I1["#1 Architecture Design"] --> I2["#2 Dockerization"]
        I1 --> I7["#7 Terraform Structure"]
        I7 --> I8["#8 VPC"]
        I8 --> I9["#9 Subnets"]
        I9 --> I10["#10 IGW & Routes"]
        I8 --> I11["#11 Security Groups"]
        I1 --> I3["#3 ECR Repo"]
    end

    subgraph S2["Sprint 2: Controller & State"]
        I8 & I9 & I11 --> I4["#4 Jenkins EC2 & EIP"]
        I7 --> I14["#14 S3 Remote State"]
        I4 --> I5["#5 Jenkins Plugins & AWS Auth"]
        I4 & I5 --> I6["#6 GitHub Webhook Integration"]
        I14 & I5 & I6 --> I15["#15 Terraform CI Pipeline"]
        I8 & I9 & I11 --> I12["#12 EKS Cluster (Cost Toggle)"]
        I12 --> I13["#13 EKS Node Group"]
    end

    subgraph S3["Sprint 3: Ansible Configuration"]
        I4 --> I16["#16 Ansible Inventory"]
        I16 --> I17["#17 Common Role"]
        I17 --> I18["#18 Docker Role"]
        I17 --> I19["#19 Kubectl Role"]
        I17 --> I20["#20 AWS CLI Role"]
        I18 & I19 & I20 --> I21["#21 Jenkins Server Role"]
        I21 --> I22["#22 Integrate Ansible into Jenkins"]
        I22 --> I23["#23 Validate Ansible Idempotency"]
    end

    subgraph S4["Sprint 4: CI/CD & Kubernetes Workloads"]
        I3 & I5 & I6 --> I24["#24 Jenkins Declarative Pipeline"]
        I24 --> I25["#25 Pytest Stage"]
        I25 --> I26["#26 Docker Build Stage"]
        I26 --> I27["#27 Trivy Security Scan"]
        I27 --> I28["#28 Push Image to ECR"]
        
        I12 & I13 --> I29["#29 K8s Namespace"]
        I29 --> I33["#33 ConfigMap & Secrets"]
        I33 --> I32["#32 MongoDB StatefulSet & PVC"]
        I33 & I28 --> I30["#30 Flask Deployment"]
        I30 --> I31["#31 ClusterIP Service"]
        I30 --> I34["#34 Liveness/Readiness Probes"]
        I30 --> I35["#35 Horizontal Pod Autoscaler"]
        I31 --> I36["#36 AWS ALB Ingress Controller"]
        I28 & I36 --> I37["#37 K8s Deploy Stage in Jenkins"]
        I37 --> I38["#38 Verify E2E Git-to-EKS Deployment"]
    end

    subgraph S5["Sprint 5: Monitoring & Alerting"]
        I38 --> I39["#39 Install Prometheus on EKS"]
        I39 --> I40["#40 App Metrics (/metrics)"]
        I39 --> I41["#41 Node Metrics (node-exporter)"]
        I39 --> I42["#42 Install Grafana on EKS"]
        I42 --> I43["#43 App KPI Dashboard"]
        I42 --> I44["#44 K8s Cluster Dashboard"]
        I39 --> I45["#45 Prometheus Alert Rules"]
        I45 --> I46["#46 Slack/Email Alerts"]
        I46 --> I47["#47 Test Alert Scenarios"]
    end

    subgraph S6["Sprint 6: Testing, Final Demo & Docs"]
        I38 --> I48["#48 App Functional Tests"]
        I2 --> I49["#49 Docker Validation Report"]
        I15 --> I50["#50 Terraform Validation Report"]
        I23 --> I51["#51 Ansible Validation Report"]
        I38 --> I52["#52 Kubernetes Validation Report"]
        I38 --> I53["#53 CI/CD E2E Validation Report"]
        I47 --> I54["#54 Monitoring Validation Report"]
        I12 --> I55["#55 AWS Cost Optimization Review"]
        I48 & I53 & I54 --> I56["#56 Complete README"]
        I1 --> I57["#57 Architecture Diagram (DONE)"]
        I24 & I37 --> I58["#58 CI/CD Pipeline Diagram"]
        I38 & I43 --> I59["#59 Collect Screenshots"]
        I56 & I59 --> I60["#60 Prepare Final Presentation"]
        I60 --> I61["#61 Prepare Viva Q&A"]
    end
```

---

## 📋 Comprehensive Sprint-by-Sprint Dependency Matrix

### **Sprint 1: Architecture, Docker & VPC Setup**

| Issue # | Issue Title | Pre-requisites (Depends On) | Blocks (What Depends on This) | Status |
| :---: | :--- | :--- | :--- | :---: |
| **#1** | Design application and DevOps architecture | None (First Step) | #2, #3, #7, #57 | ✅ **DONE** |
| **#2** | Validate application Dockerization | #1 | #26, #49 | ✅ **DONE** |
| **#3** | Create AWS ECR repository | #1, #7 | #28, #30 | ✅ **DONE** |
| **#7** | Create Terraform project structure | #1 | #8, #11, #14 | ✅ **DONE** |
| **#8** | Provision AWS VPC using Terraform | #7 | #9, #10, #11 | ✅ **DONE** |
| **#9** | Create public and private subnets | #8 | #4, #12 | ✅ **DONE** |
| **#10** | Configure Internet Gateway and Route Tables | #8, #9 | #4, #12, #36 | ✅ **DONE** |
| **#11** | Configure Security Groups | #8 | #4, #12, #30, #32 | ✅ **DONE** |

---

### **Sprint 2: Terraform & AWS Infrastructure**

| Issue # | Issue Title | Pre-requisites (Depends On) | Blocks (What Depends on This) | Status |
| :---: | :--- | :--- | :--- | :---: |
| **#4** | Provision Jenkins EC2 server | #9, #10, #11 | #5, #16 | ✅ **DONE** |
| **#14** | Configure Terraform remote state in S3 | #7 | #15, #50 | ✅ **DONE** |
| **#5** | Configure Jenkins plugins and AWS credentials | #4 | #6, #15, #24 | 🟡 **IN REVIEW** (Needs live check) |
| **#6** | Integrate the GitHub repository with Jenkins | #4, #5 | #15, #24, #38 | 🟡 **IN REVIEW** (Needs Webhook) |
| **#15** | Integrate Terraform execution with Jenkins | #5, #6, #14 | #22, #50 | 🟡 **IN REVIEW** (Needs Build #1) |
| **#12** | Provision AWS EKS cluster | #9, #10, #11 | #13, #29 | ⏸️ **CODE DONE** (Paused for cost) |
| **#13** | Provision EKS managed node group | #12 | #29, #30, #32 | ⏸️ **CODE DONE** (Paused for cost) |

> [!IMPORTANT]
> **EKS Cost Control Rule (#12 & #13)**: Keep `enable_eks = false` and `enable_nat_gateway = false` in `terraform.tfvars` until the team is ready to deploy Kubernetes workloads in **Sprint 4**. This saves ~$175/month during Sprints 2 & 3.

---

### **Sprint 3: Ansible Configuration Management**

| Issue # | Issue Title | Pre-requisites (Depends On) | Blocks (What Depends on This) | Status |
| :---: | :--- | :--- | :--- | :---: |
| **#16** | Create Ansible inventory | #4 (Needs live IP) | #17, #21 | 🟡 **CODE READY** (hosts.ini updated) |
| **#17** | Create common configuration role | #16 | #18, #19, #20 | 🟡 **CODE READY** (roles/common) |
| **#18** | Install Docker using Ansible | #17 | #21, #26 | ⏳ **PENDING** |
| **#19** | Install kubectl using Ansible | #17 | #21, #37 | ⏳ **PENDING** |
| **#20** | Install AWS CLI using Ansible | #17 | #21, #28 | 🟡 **CODE READY** (roles/aws_cli) |
| **#21** | Configure Jenkins server using Ansible | #17, #18, #19, #20 | #22 | 🟡 **CODE READY** (roles/jenkins) |
| **#22** | Integrate Ansible stage into Jenkins | #15, #21 | #23, #51 | ⏳ **PENDING** |
| **#23** | Validate Ansible idempotency | #21, #22 | #51 | ⏳ **PENDING** |

---

### **Sprint 4: Jenkins CI/CD & Kubernetes EKS Workloads**

| Issue # | Issue Title | Pre-requisites (Depends On) | Blocks (What Depends on This) | Status |
| :---: | :--- | :--- | :--- | :---: |
| **#24** | Create Jenkins declarative pipeline | #5, #6 | #25, #26 | ⏳ **PENDING** |
| **#25** | Add application test stage (pytest) | #24 | #26 | ⏳ **PENDING** |
| **#26** | Add Docker build stage | #18, #25 | #27 | ⏳ **PENDING** |
| **#27** | Add Trivy security scanning | #26 | #28 | ⏳ **PENDING** |
| **#28** | Push Docker image to AWS ECR | #3, #20, #27 | #30, #37 | ⏳ **PENDING** |
| **#12 & #13 Act.** | **Activate EKS Cluster & Nodes (`enable_eks=true`)** | #9, #10, #11 | #29 | ⏸️ **TRIGGER SPRINT 4** |
| **#29** | Create Kubernetes namespace (`lumora-prod`) | #12, #13 | #30, #32, #33 | ⏳ **PENDING** |
| **#33** | Configure ConfigMap and Secrets | #29 | #30, #32 | ⏳ **PENDING** |
| **#32** | Configure MongoDB workload (StatefulSet + EBS) | #11, #29, #33 | #30 | ⏳ **PENDING** |
| **#30** | Create Flask Deployment | #28, #29, #32, #33 | #31, #34, #35 | ⏳ **PENDING** |
| **#31** | Create Kubernetes Service (ClusterIP) | #30 | #36 | ⏳ **PENDING** |
| **#34** | Configure liveness and readiness probes | #30 | #37 | ⏳ **PENDING** |
| **#35** | Configure Horizontal Pod Autoscaler (HPA) | #30 | #37, #52 | ⏳ **PENDING** |
| **#36** | Configure AWS Load Balancer / Ingress | #10, #11, #31 | #37, #38 | ⏳ **PENDING** |
| **#37** | Add Kubernetes deploy stage to Jenkins | #19, #28, #36 | #38, #53 | ⏳ **PENDING** |
| **#38** | Verify end-to-end GitHub → Jenkins → EKS deployment | #37 | #39, #48, #53 | ⏳ **PENDING** |

---

### **Sprint 5: Prometheus, Grafana & Alerts**

| Issue # | Issue Title | Pre-requisites (Depends On) | Blocks (What Depends on This) | Status |
| :---: | :--- | :--- | :--- | :---: |
| **#39** | Install Prometheus on EKS (Helm) | #38 | #40, #41, #45 | ⏳ **PENDING** |
| **#40** | Configure application metrics collection | #39, #30 | #43 | ⏳ **PENDING** |
| **#41** | Configure Kubernetes node metrics | #39, #13 | #44 | ⏳ **PENDING** |
| **#42** | Install Grafana on EKS (Helm) | #39 | #43, #44 | ⏳ **PENDING** |
| **#43** | Build application Grafana dashboard | #40, #42 | #47, #54 | ⏳ **PENDING** |
| **#44** | Build Kubernetes infrastructure dashboard | #41, #42 | #47, #54 | ⏳ **PENDING** |
| **#45** | Configure Prometheus alerts | #39 | #46 | ⏳ **PENDING** |
| **#46** | Configure deployment failure notifications (Slack/Email) | #45, #37 | #47 | ⏳ **PENDING** |
| **#47** | Test monitoring and alerting | #43, #44, #46 | #54 | ⏳ **PENDING** |

---

### **Sprint 6: Testing, Documentation & Final Demo**

| Issue # | Issue Title | Pre-requisites (Depends On) | Blocks (What Depends on This) | Status |
| :---: | :--- | :--- | :--- | :---: |
| **#48** | Execute application functional tests | #38 | #56, #60 | ⏳ **PENDING** |
| **#49** | Execute Docker validation | #2 | #56, #60 | ⏳ **PENDING** |
| **#50** | Execute Terraform validation | #14, #15 | #56, #60 | ⏳ **PENDING** |
| **#51** | Execute Ansible validation | #23 | #56, #60 | ⏳ **PENDING** |
| **#52** | Execute Kubernetes deployment tests | #35, #38 | #56, #60 | ⏳ **PENDING** |
| **#53** | Execute CI/CD end-to-end test | #38 | #56, #60 | ⏳ **PENDING** |
| **#54** | Execute monitoring and alert tests | #47 | #56, #60 | ⏳ **PENDING** |
| **#55** | AWS Cost Optimization Review | #12, #13 | #56, #60 | 🟡 **PARTIALLY DONE** (EIP/EKS toggles) |
| **#56** | Complete README documentation | #48–#55 | #60 | ⏳ **PENDING** |
| **#57** | Create architecture diagram | #1 | #56, #60 | ✅ **DONE** (`architecture_diagram_v2.png`) |
| **#58** | Create CI/CD pipeline diagram | #24, #37 | #56, #60 | ⏳ **PENDING** |
| **#59** | Collect project screenshots | All Sprints | #60 | ⏳ **PENDING** |
| **#60** | Prepare final presentation | #56, #58, #59 | #61 | ⏳ **PENDING** |
| **#61** | Prepare viva questions and answers | #60 | Final Submission | ⏳ **PENDING** |

---

## 🎯 Step-by-Step Chronological Execution Order

To avoid team members being blocked, execute tasks in the following exact sequence:

### **Phase 1: Close Out Sprint 2 Verification (Immediate Next Step)**
1. **Power On Controller**: Run `aws ec2 start-instances --instance-ids i-03e7a9837cadbced6`.
2. **Setup Webhook (#6)**: In GitHub repository Settings ➔ Webhooks, add `http://32.195.28.191:8080/github-webhook/`.
3. **Trigger Build #1 (#15)**: Open `http://32.195.28.191:8080`, run pipeline `lumora-ecommerce-terraform-ci`.
4. **Verify ECR Access (#5)**: Verify pipeline validates AWS IAM identity and checks out source code cleanly.
5. **Project Board Update**: Once Build #1 is green, move **#5, #6, and #15 to `Done`**.

---

### **Phase 2: Sprint 3 (Ansible Automation Execution)**
1. **Inventory Verification (#16)**: Teammates pull latest `main` with `32.195.28.191` in `ansible/inventory/hosts.ini`.
2. **Execute Playbook (#17, #20, #21)**:
   ```bash
   ansible-playbook -i inventory/hosts.ini playbooks/setup_jenkins.yml
   ```
3. **Add Docker & Kubectl Roles (#18, #19)**: Create roles for Docker daemon and kubectl CLI on the Jenkins controller.
4. **Test Idempotency (#23)**: Run the playbook a second time. Verify `changed=0`, `failed=0`.
5. **Project Board Update**: Move **#16, #17, #18, #19, #20, #21, #22, #23 to `Done`**.

---

### **Phase 3: Sprint 4 (Activate EKS & Deploy Microservices)**
1. **Enable EKS (#12, #13)**: In `terraform/terraform.tfvars`, set `enable_eks = true` and `enable_nat_gateway = true`. Run `terraform apply`.
2. **Verify Cluster Access**: Run `aws eks update-kubeconfig --region us-east-1 --name lumora-ecommerce-prod-cluster`. Test `kubectl get nodes`. Move **#12 and #13 to `Done`**.
3. **Author Kubernetes Manifests (`k8s/`)**:
   - `00-namespace.yaml` (#29)
   - `01-configmap-secrets.yaml` (#33)
   - `02-mongodb-statefulset.yaml` & EBS PVC (#32)
   - `03-flask-deployment.yaml` with probes & HPA (#30, #34, #35)
   - `04-service-ingress.yaml` with AWS ALB Ingress Controller (#31, #36)
4. **Build Jenkins Full App Pipeline (#24–#28, #37)**:
   - Create multi-stage `Jenkinsfile`: `Test` ➔ `Build` ➔ `Trivy Scan` ➔ `ECR Push` ➔ `Deploy to EKS`.
5. **End-to-End Test (#38)**: Push commit to `main`, watch Jenkins trigger, build container, and deploy rolling update to EKS.
6. **Project Board Update**: Move **#24 through #38 to `Done`**.

---

### **Phase 4: Sprint 5 (Observability & Alerts)**
1. **Deploy Prometheus & Grafana (#39, #42)** via Helm onto EKS cluster.
2. **Configure Metrics Exporters (#40, #41)**: Flask `/metrics` endpoint & `node-exporter`.
3. **Import Dashboards (#43, #44)**: Application KPI Dashboard and Node Resource Dashboard.
4. **Alert Rules (#45, #46, #47)**: Configure Slack notifications on high latency or pod crash loops.
5. **Project Board Update**: Move **#39 through #47 to `Done`**.

---

### **Phase 5: Sprint 6 (Evidence Gathering, Tear Down & Final Pitch)**
1. **Run Validation Test Suites (#48–#54)** and save evidence into `project_artifacts/`.
2. **Cost Optimization Review (#55)**: Document cost savings achieved with EKS/NAT toggles and Elastic IP.
3. **Generate CI/CD Diagram (#58)** and collect all screenshots (#59).
4. **Tear Down Expensive Resources**: Set `enable_eks = false` and `enable_nat_gateway = false` in `terraform.tfvars` and run `terraform apply` to avoid further billing.
5. **Presentation & Viva Prep (#60, #61)**: Complete slide deck and viva defense document.
6. **Project Board Update**: Move **#48 through #61 to `Done`**.
