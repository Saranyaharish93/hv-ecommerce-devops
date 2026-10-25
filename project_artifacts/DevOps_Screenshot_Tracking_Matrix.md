# Lumora E-Commerce DevOps Platform: Screenshot Tracking Matrix

This internal tracking matrix is designed for project team members to track, capture, verify, and organize all visual proof artifacts during live AWS deployment.

---

## 1. Directory Structure Standards

All captured screenshots must be saved under `project_artifacts/screenshots/` organized by component domain:

```text
project_artifacts/screenshots/
├── jenkins/
│   ├── 01_jenkins_dashboard.png
│   ├── 02_pipeline_stage_view_success.png
│   ├── 03_terraform_apply_approval_gate.png
│   ├── 04_trivy_scan_console.png
│   └── 05_github_webhook_delivery.png
├── terraform/
│   ├── 01_vpc_subnets.png
│   ├── 02_s3_state_bucket.png
│   ├── 03_secrets_manager_entry.png
│   ├── 04_aws_budgets_dashboard.png
│   └── 05_terraform_plan_output.png
├── ansible/
│   ├── 01_ansible_first_run.png
│   ├── 02_ansible_idempotency_proof.png
│   └── 03_tool_versions_verification.png
├── kubernetes/
│   ├── 01_eks_nodes_active.png
│   ├── 02_kubectl_get_all.png
│   ├── 03_pvc_bound_status.png
│   ├── 04_hpa_active_metrics.png
│   └── 05_alb_ingress_storefront.png
├── monitoring/
│   ├── 01_metrics_server_nodes.png
│   ├── 02_prometheus_targets_up.png (Prometheus_targethealth.png)
│   ├── 03_grafana_app_kpi.png
│   ├── 04_grafana_cluster_infra.png (Grafana_dashboard.png)
│   ├── 05_alertmanager_notification.png (Prometheus_alerts.png)
│   └── Grafana_homepage.png
└── security_finops/
    ├── 01_infracost_report_jenkins.png
    ├── 02_trivy_scan_output.png
    ├── 03_aws_secrets_manager.png
    ├── 04_aws_budgets_alerts.png
    └── 05_non_root_user_exec.png
```

---

## 2. Master Platform Screenshot Matrix

| Ref ID | Status | Concept Demonstrated | Target Documentation File | Expected File Path |
| :---: | :---: | :--- | :--- | :--- |
| **SS-01** | [ ] | AWS VPC Subnets and Route Table Topology | `devops/terraform.md` (Section 3) | `project_artifacts/screenshots/terraform/01_vpc_subnets.png` |
| **SS-02** | [ ] | S3 Remote State Bucket and Lockfile | `devops/terraform.md` (Section 4) | `project_artifacts/screenshots/terraform/02_s3_state_bucket.png` |
| **SS-03** | [ ] | EC2 Jenkins Controller Dashboard | `devops/jenkins.md` (Section 1) | `project_artifacts/screenshots/jenkins/01_jenkins_dashboard.png` |
| **SS-04** | [ ] | Ansible Playbook Idempotent Proof (`changed=0`) | `devops/ansible.md` (Section 5) | `project_artifacts/screenshots/ansible/02_ansible_idempotency_proof.png` |
| **SS-05** | [ ] | Jenkins Declarative Pipeline Complete Run | `devops/jenkins.md` (Section 2) | `project_artifacts/screenshots/jenkins/02_pipeline_stage_view_success.png` |
| **SS-06** | [ ] | Infracost Cost Breakdown Report in Jenkins | `devops/security-and-finops.md` (Section 6) | `project_artifacts/screenshots/security_finops/01_infracost_report_jenkins.png` |
| **SS-07** | [ ] | Trivy Vulnerability Scan Output in Jenkins | `devops/jenkins.md` (Section 3) | `project_artifacts/screenshots/jenkins/04_trivy_scan_console.png` |
| **SS-08** | [ ] | EKS Cluster Nodes Ready in AWS Console | `devops/kubernetes.md` (Section 1) | `project_artifacts/screenshots/kubernetes/01_eks_nodes_active.png` |
| **SS-09** | [ ] | Kubernetes Pods, StatefulSet, and Services | `devops/kubernetes.md` (Section 3) | `project_artifacts/screenshots/kubernetes/02_kubectl_get_all.png` |
| **SS-10** | [ ] | Horizontal Pod Autoscaler Active & Reporting | `devops/kubernetes.md` (Section 6) | `project_artifacts/screenshots/kubernetes/04_hpa_active_metrics.png` |
| **SS-11** | [ ] | AWS Secrets Manager Configuration | `devops/terraform.md` (Section 6) | `project_artifacts/screenshots/terraform/03_secrets_manager_entry.png` |
| **SS-12** | [ ] | Application Storefront Live via Ingress ALB | `devops/kubernetes.md` (Section 7) | `project_artifacts/screenshots/kubernetes/05_alb_ingress_storefront.png` |
| **SS-13** | [x] | Prometheus Server Targets Scraping Health | `devops/monitoring.md` (Section 5.1) | `project_artifacts/screenshots/monitoring/02_prometheus_targets_up.png` |
| **SS-14** | [x] | Grafana Application and Node KPI Dashboard | `devops/monitoring.md` (Section 7.1) | `project_artifacts/screenshots/monitoring/04_grafana_cluster_infra.png` |
| **SS-15** | [ ] | AWS Budgets Console Spending & Forecast | `devops/terraform.md` (Section 6) | `project_artifacts/screenshots/terraform/04_aws_budgets_dashboard.png` |

---

## 3. Component Deep-Dive Checklists

### 3.1. Jenkins CI/CD Automation (`devops/jenkins.md`)

| Ref ID | Status | Concept Demonstrated | Section Reference | Target Image File Path |
| :---: | :---: | :--- | :--- | :--- |
| **JK-01** | [ ] | Jenkins Controller Dashboard | Section 1 (Architecture & Controller) | `project_artifacts/screenshots/jenkins/01_jenkins_dashboard.png` |
| **JK-02** | [ ] | 16-Stage Pipeline Complete Success | Section 2 (Declarative Pipeline Overview) | `project_artifacts/screenshots/jenkins/02_pipeline_stage_view_success.png` |
| **JK-03** | [ ] | Manual Approval Gate Modal | Section 3 (Stage 9 & 10 Approval) | `project_artifacts/screenshots/jenkins/03_terraform_apply_approval_gate.png` |
| **JK-04** | [ ] | Infracost Cost Breakdown Output | Section 3 (Stage 8 FinOps Estimation) | `project_artifacts/screenshots/security_finops/01_infracost_report_jenkins.png` |
| **JK-05** | [ ] | Trivy Container Security Vulnerability Scan | Section 3 (Stage 14 Security Scan) | `project_artifacts/screenshots/jenkins/04_trivy_scan_console.png` |
| **JK-06** | [ ] | GitHub Webhook HTTP 200 Delivery | Section 4 (GitHub Webhook Integration) | `project_artifacts/screenshots/jenkins/05_github_webhook_delivery.png` |

### 3.2. Terraform Infrastructure as Code (`devops/terraform.md`)

| Ref ID | Status | Concept Demonstrated | Section Reference | Target Image File Path |
| :---: | :---: | :--- | :--- | :--- |
| **TF-01** | [ ] | AWS VPC Subnets and Route Tables | Section 3 (AWS 3-Tier Network Topology) | `project_artifacts/screenshots/terraform/01_vpc_subnets.png` |
| **TF-02** | [ ] | S3 Remote State Bucket and Lockfile | Section 4 (State Management & Locking) | `project_artifacts/screenshots/terraform/02_s3_state_bucket.png` |
| **TF-03** | [ ] | AWS Secrets Manager Configuration | Section 6.1 (Secrets Management) | `project_artifacts/screenshots/terraform/03_secrets_manager_entry.png` |
| **TF-04** | [ ] | AWS Budgets $25 Monthly Cap Alarms | Section 6.2 (AWS Budgets) | `project_artifacts/screenshots/terraform/04_aws_budgets_dashboard.png` |
| **TF-05** | [ ] | Clean `terraform plan` CLI Output | Section 7 (Cost Toggles & Execution) | `project_artifacts/screenshots/terraform/05_terraform_plan_output.png` |

### 3.3. Ansible Configuration Management (`devops/ansible.md`)

| Ref ID | Status | Concept Demonstrated | Section Reference | Target Image File Path |
| :---: | :---: | :--- | :--- | :--- |
| **AN-01** | [ ] | Tool Versions Verification | Section 3 (Deep-Dive into 7 Roles) | `project_artifacts/screenshots/ansible/03_tool_versions_verification.png` |
| **AN-02** | [ ] | Initial Playbook Convergence | Section 5 (Idempotency First Pass) | `project_artifacts/screenshots/ansible/01_ansible_first_run.png` |
| **AN-03** | [ ] | Idempotency Verification (`changed=0`) | Section 5 (Idempotency Second Pass) | `project_artifacts/screenshots/ansible/02_ansible_idempotency_proof.png` |

### 3.4. Kubernetes Orchestration on EKS (`devops/kubernetes.md`)

| Ref ID | Status | Concept Demonstrated | Section Reference | Target Image File Path |
| :---: | :---: | :--- | :--- | :--- |
| **K8S-01** | [ ] | EKS Worker Nodes Ready | Section 1 (EKS Cluster Architecture) | `project_artifacts/screenshots/kubernetes/01_eks_nodes_active.png` |
| **K8S-02** | [ ] | Workloads in `lumora-prod` | Section 3 (Manifest Deep-Dive) | `project_artifacts/screenshots/kubernetes/02_kubectl_get_all.png` |
| **K8S-03** | [ ] | PersistentVolumeClaim Bound | Section 3 (Stateful Database Tier) | `project_artifacts/screenshots/kubernetes/03_pvc_bound_status.png` |
| **K8S-04** | [ ] | HPA Metrics Reporting Active | Section 6 (HPA Autoscaling) | `project_artifacts/screenshots/kubernetes/04_hpa_active_metrics.png` |
| **K8S-05** | [ ] | Live Storefront via ALB Ingress | Section 7 (AWS ALB Ingress) | `project_artifacts/screenshots/kubernetes/05_alb_ingress_storefront.png` |

### 3.5. Observability & Monitoring (`devops/monitoring.md`)

| Ref ID | Status | Concept Demonstrated | Section Reference | Target Image File Path |
| :---: | :---: | :--- | :--- | :--- |
| **MON-01**| [ ] | Kubernetes Metrics Server Running | Section 2 (Metrics Server Bootstrap) | `project_artifacts/screenshots/monitoring/01_metrics_server_nodes.png` |
| **MON-02**| [x] | Prometheus Scrape Targets Healthy | Section 5.1 (Target Scraping Verification) | `project_artifacts/screenshots/monitoring/02_prometheus_targets_up.png` |
| **MON-03**| [ ] | Grafana Application KPI Visuals | Section 7.1 (Application KPI Dashboard) | `project_artifacts/screenshots/monitoring/03_grafana_app_kpi.png` |
| **MON-04**| [x] | Grafana Node Saturation Visuals | Section 7.1 (Infrastructure Dashboard) | `project_artifacts/screenshots/monitoring/04_grafana_cluster_infra.png` |
| **MON-05**| [x] | Alertmanager / Prometheus Alert Rules | Section 6.1 (Alerts Live Verification) | `project_artifacts/screenshots/monitoring/05_alertmanager_notification.png` |

### 3.6. Shift-Left Security & FinOps Governance (`devops/security-and-finops.md`)

| Ref ID | Status | Concept Demonstrated | Section Reference | Target Image File Path |
| :---: | :---: | :--- | :--- | :--- |
| **SEC-01**| [ ] | Infracost Breakdown Report | Section 6 (Infracost Pipeline Analysis) | `project_artifacts/screenshots/security_finops/01_infracost_report_jenkins.png` |
| **SEC-02**| [ ] | Trivy Container Security Scan | Section 2 (Trivy Image Scan) | `project_artifacts/screenshots/security_finops/02_trivy_scan_output.png` |
| **SEC-03**| [ ] | AWS Secrets Manager Configuration | Section 4 (Secrets Governance) | `project_artifacts/screenshots/security_finops/03_aws_secrets_manager.png` |
| **SEC-04**| [ ] | AWS Budgets $25 Limit Alarms | Section 7 (AWS Budgets) | `project_artifacts/screenshots/security_finops/04_aws_budgets_alerts.png` |
| **SEC-05**| [ ] | Container Non-Root User Verification | Section 3 (Container Hardening) | `project_artifacts/screenshots/security_finops/05_non_root_user_exec.png` |

---

## 4. Screenshot Capture Guidelines

1. **Resolution**: Standardize on minimum 1080p (1920x1080) browser or terminal window size.
2. **Clarity**: Crop out unrelated background browser tabs, operating system taskbars, and personal identifiers.
3. **Security**: Ensure no cleartext AWS access keys, SSH private keys, or passwords appear in terminal outputs or URL query parameters.
4. **File Naming**: Use exact filenames specified above to ensure seamless auto-rendering in markdown documentation once captured.
