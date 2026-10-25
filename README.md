# Lumora E-Commerce DevOps Capstone

[![Production Storefront](https://img.shields.io/badge/Live%20Storefront-lumora.thiagarajanb.dpdns.org-2ea44f?style=flat-square&logo=googlechrome&logoColor=white)](https://lumora.thiagarajanb.dpdns.org/)
[![AWS EKS](https://img.shields.io/badge/Kubernetes-AWS%20EKS%20v1.30-326CE5?style=flat-square&logo=kubernetes&logoColor=white)](devops/kubernetes.md)
[![Jenkins CI/CD](https://img.shields.io/badge/CI%2FCD-Jenkins%2016--Stage-D24939?style=flat-square&logo=jenkins&logoColor=white)](devops/jenkins.md)
[![Terraform](https://img.shields.io/badge/IaC-Terraform%20v1.5+-7B42BC?style=flat-square&logo=terraform&logoColor=white)](devops/terraform.md)
[![Ansible](https://img.shields.io/badge/Automation-Ansible-EE0000?style=flat-square&logo=ansible&logoColor=white)](devops/ansible.md)
[![Status](https://img.shields.io/badge/Capstone%20Status-100%25%20Completed-brightgreen?style=flat-square)](devops/README.md)

Lumora is a full-stack e-commerce web application built with Python, Flask, and MongoDB. The repository combines a working storefront with the DevOps assets required for an end-to-end capstone project covering CI/CD, cloud infrastructure automation, Docker, Jenkins, Terraform, Ansible, Kubernetes, and observability.

This project is designed to demonstrate a realistic engineering lifecycle: build a functional online store, containerize the application, automate validation and security checks, provision cloud infrastructure, and deploy to a Kubernetes-based environment.

> **Key Presentation & Navigation Links**:
> - **Live Storefront Endpoint**: [https://lumora.thiagarajanb.dpdns.org/](https://lumora.thiagarajanb.dpdns.org/)
> - **Master DevOps Suite & Presentation**: [DevOps Platform Master Guide](devops/README.md)
> - **Viva Technical Defense Guide**: [DevOps Capstone Viva Prep Guide](project_artifacts/DevOps_Capstone_Viva_Preparation_Guide.md)

---

## Project Overview

*Direct Artifact Reference: [`project_artifacts/Lumora_E-Commerce_Architecture_v3.png`](project_artifacts/Lumora_E-Commerce_Architecture_v3.png)*

![Lumora E-Commerce DevOps Platform Architecture](project_artifacts/Lumora_E-Commerce_Architecture_v3.png)
Lumora is a demo electronics storefront with customer browsing, product discovery, cart and checkout flow, order tracking, newsletter-like contact interactions, and administrative reporting. The repository supports both application development and DevOps execution, making it suitable for showcasing a complete software delivery pipeline.

The project includes:
- a Flask application backed by MongoDB
- local Docker and Docker Compose orchestration
- automated application tests
- Jenkins pipeline automation
- Terraform infrastructure provisioning
- Ansible configuration management
- Kubernetes manifests for deployment
- project documentation and sprint artifacts

---

## Objective of the Project

#### 1. Source Control & Collaboration
- **Developer Workflow**: Developers work on feature branches and submit Pull Requests to the `main` branch on GitHub.
- **Automated Triggers**: GitHub Webhooks trigger the Jenkins declarative pipeline on every push or merged PR.

#### 2. Automation, CI & Security (Jenkins on AWS EC2)
- **Controller Host**: Jenkins runs on an AWS EC2 instance in a dedicated management security group, fully configured and hardened using **Ansible playbooks** (automating Docker Engine, `kubectl`, AWS CLI, and security tools).
- **Declarative Pipeline Stages**:
  1. `Checkout`: Pulls the latest code repository from GitHub.
  2. `Pytest`: Runs automated unit and functional test suites under `tests/`.
  3. `Trivy Scan`: Scans application files and container dependencies for security vulnerabilities.
  4. `Docker BuildKit`: Builds optimized, secure container images with non-root user (`appuser`).
  5. `Push Image`: Tags images with build numbers and pushes to **Amazon ECR**.
  6. `Terraform Plan/Apply`: Provisions and manages AWS VPC, subnets, and EKS resources with remote state locking.
  7. `Ansible`: Manages host configurations idempotently.
  8. `Deploy to EKS`: Applies rolling updates to Kubernetes workloads using `kubectl`.

#### 3. Artifacts & IaC State Management
- **Amazon ECR**: Serves as the private container registry for immutable, semantically tagged application images (`lumora-flask`).
- **Amazon S3 & DynamoDB**: Provides secure remote state storage and state locking for Terraform to enable seamless team collaboration.

#### 4. AWS Production Network (VPC `10.0.0.0/16`)
- **Multi-AZ Resilience**: Network resources are distributed across **Availability Zone A** and **Availability Zone B**.
- **Public Subnets (`10.0.1.0/24`, `10.0.2.0/24`)**:
  - **Internet Gateway (IGW)** for external inbound/outbound connectivity.
  - **Dual-AZ NAT Gateways** providing secure outbound internet access for private workloads.
  - **AWS Application Load Balancer (ALB)** handling TLS/HTTPS termination on port `443`.
  - **Jenkins EC2 / Bastion Host**.
- **Private Subnets (`10.0.11.0/24`, `10.0.12.0/24`)**:
  - Isolated from direct public internet exposure.
  - Hosts **EKS Managed Node Groups** and all application/database pods.

#### 5. Kubernetes Workloads (Amazon EKS — Namespace `lumora-prod`)
- **ALB Ingress Controller**: Routes incoming external traffic to the internal `lumora-app-service` (ClusterIP: `5000`).
- **Flask Application Deployment**:
  - Multi-replica Python 3.12 Flask app running behind **Gunicorn**.
  - Configured with `readinessProbe` and `livenessProbe` monitoring `/health`.
  - Scaled dynamically (2 to 10 replicas) using the **Horizontal Pod Autoscaler (HPA)** based on CPU/memory utilization.
  - Environment configuration managed via Kubernetes `ConfigMap` and secrets via `Kubernetes Secrets`.
- **Database Workload (MongoDB 7.0)**:
  - Deployed as a dedicated `MongoDB StatefulSet` in the private subnet.
  - Internal communication via `mongo-service` (ClusterIP: `27017`) — completely isolated from public access.
  - Data persistence guaranteed using **PersistentVolumeClaim (PVC)** bound to high-performance **Amazon EBS `gp3` volumes** via the **AWS EBS CSI Driver**.

#### 6. Observability, Alerting & Operations
- **Prometheus**: Time Series Database scraping metrics on a 15-second interval from:
  - `Flask App (/metrics)` & `Flask App (/health)`
  - `node-exporter (/metrics)` on EC2 worker nodes
  - `kube-state-metrics (/metrics)` for pod, deployment, and cluster health
- **Grafana**: Visualizes real-time performance dashboards:
  - **Application KPI Dashboard**: HTTP request rate, response latency, order transactions, error rates.
  - **Infrastructure Dashboard**: Node CPU/RAM utilization, pod restart counts, disk I/O.
- **Alertmanager & Incident Management**:
  - Triggers operational alerts on latency thresholds, pod crash loops, and resource exhaustion.
  - Routes notifications to **Slack**, **Email**, and **PagerDuty**.
  - Integrates Jenkins pipeline build failure notifications.
The objective of this capstone is to implement an end-to-end DevOps workflow for a real-world application. The project moves from app development and source control to containerization, infrastructure as code, automation, deployment orchestration, and monitoring.

It demonstrates how the following work together in practice:
- Application development with Flask
- Data storage with MongoDB
- Containerization with Docker
- CI/CD with Jenkins
- Provisioning with Terraform
- Automation with Ansible
- Deployment with Kubernetes
- Monitoring with Prometheus and Grafana concepts

---

## Live Storefront & DevOps Implementation Proofs

### 1. Live E-Commerce Storefront on AWS EKS & Cloudflare
*Live Public Endpoint: [https://lumora.thiagarajanb.dpdns.org/](https://lumora.thiagarajanb.dpdns.org/)*

| Storefront Homepage | Product Catalog & Inventory |
| :---: | :---: |
| ![Homepage](project_artifacts/screenshots/storefront/01_homepage.png) | ![Product Catalog](project_artifacts/screenshots/storefront/02_shop_catalog.png) |

| Shopping Cart & Checkout | User Authentication Portal |
| :---: | :---: |
| ![Shopping Cart](project_artifacts/screenshots/storefront/03_shopping_cart.png) | ![User Login](project_artifacts/screenshots/storefront/04_login_page.png) |

---

### 2. CI/CD Orchestration & Shift-Left DevSecOps (Jenkins & Ansible)

| Jenkins Web Controller Dashboard | 16-Stage Declarative Pipeline Execution |
| :---: | :---: |
| ![Jenkins Web Dashboard](project_artifacts/screenshots/jenkins/Jenkins_Homepage.png) | ![Pipeline Stage View](project_artifacts/screenshots/jenkins/02_pipeline_stage_view_success.png) |

| Shift-Left FinOps Cost Estimation (Infracost) | Shift-Left Container Security (Trivy CVE Scan) |
| :---: | :---: |
| ![Infracost Cost Analysis](project_artifacts/screenshots/security_finops/01_infracost_report_jenkins.png) | ![Trivy Security Scan](project_artifacts/screenshots/jenkins/04_trivy_scan_console.png) |

---

### 3. AWS Cloud Infrastructure & Kubernetes Workloads

| AWS Multi-AZ VPC Architecture | Amazon EKS Workload Console |
| :---: | :---: |
| ![AWS VPC](project_artifacts/screenshots/aws/vpc.png) | ![EKS Workload Status](project_artifacts/screenshots/aws/eks_workload_status.png) |

| AWS Application Load Balancer (ALB) | Kubernetes Pods & StatefulSets (`lumora-prod`) |
| :---: | :---: |
| ![AWS ALB](project_artifacts/screenshots/aws/alb.png) | ![Kubernetes Workloads](project_artifacts/screenshots/kubernetes/02_kubectl_get_all.png) |

#### Horizontal Pod Autoscaler (HPA v2) Metric Reporting
![Horizontal Pod Autoscaler](project_artifacts/screenshots/kubernetes/04_hpa_active_metrics.png)

---

## Application Features

### Customer-facing features & Visual Storefront Walkthrough

| Storefront Landing & Hero Banner (`/`) | Product Catalog & Inventory Filtering (`/shop`) |
| :---: | :---: |
| ![Homepage](project_artifacts/screenshots/storefront/01_homepage.png) | ![Shop Catalog](project_artifacts/screenshots/storefront/02_shop_catalog.png) |

| Curated Product Collections (`/collections`) | Brand Story & About (`/story`) |
| :---: | :---: |
| ![Collections](project_artifacts/screenshots/storefront/05_collections.png) | ![Brand Story](project_artifacts/screenshots/storefront/07_brand_story.png) |

| Interactive Cart & Order Calculation (`/cart`) | Customer Saved Wishlist |
| :---: | :---: |
| ![Shopping Cart](project_artifacts/screenshots/storefront/03_shopping_cart.png) | ![Wishlist](project_artifacts/screenshots/storefront/E-commerce_portal_login_wishlist.png) |

| Customer Profile & Account Management | Order Tracking & Status Journey |
| :---: | :---: |
| ![Profile](project_artifacts/screenshots/storefront/E-commerce_portal_profilepage.png) | ![Order Journey](project_artifacts/screenshots/storefront/E-commerce_portal_orderjourney-1.png) |

| Customer Support & Inquiries (`/contact`) | Profile Settings & Address Book (`/profile/edit`) |
| :---: | :---: |
| ![Contact](project_artifacts/screenshots/storefront/06_contact_page.png) | ![Profile Edit](project_artifacts/screenshots/storefront/E-commerce_portal_profileedit.png) |

| Authentication Portal (`/login`) | Custom Domain & SSL Verification |
| :---: | :---: |
| ![Login](project_artifacts/screenshots/storefront/04_login_page.png) | ![DNS Mapped SSL](project_artifacts/screenshots/storefront/E-commerce_portal_DNS_mapped-1.png) |

- User registration, session-based authentication, and role-aware access
- Password reset flow with simulated email tracking
- Product catalog, search, and category browsing
- Product detail pages with ratings and customer review capability
- Wishlist support and shopping cart management
- Checkout flow with demo payment methods and invoice generation
- Order history, detailed order lifecycle tracking, and status updates
- Responsive UI optimized for desktop, tablet, and mobile displays

### Admin Features & Back-Office Walkthrough

| Back-Office Analytics & Metric Overview (`/admin`) | Product Catalog Management & Inventory Controls (`/admin/products`) |
| :---: | :---: |
| ![Admin Dashboard](project_artifacts/screenshots/storefront/E-commerce_admin_homepage.png) | ![Product Management](project_artifacts/screenshots/storefront/E-commerce_admin_product_management.png) |

| Customer & User Management (`/admin/customers`) | Financial Reports & Revenue Analytics (`/admin/reports`) |
| :---: | :---: |
| ![User Management](project_artifacts/screenshots/storefront/E-commerce_admin_user_management.png) | ![Financial Reports Dashboard](project_artifacts/screenshots/storefront/E-commerce_admin_finance_dashboard.png) |

- **Admin dashboard with key metrics**: High-level platform health, total sales revenue, active customer count, order volumes, and real-time operational status.
- **Product management**: Comprehensive catalog controls allowing administrators to add new items, update prices, manage stock quantities, adjust categories, and delete obsolete listings.
- **Image upload support**: Secure multi-part image ingestion for product listings and promotional banners.
- **Customer management and activation toggling**: Administrative oversight of user accounts, email verification status, and one-click account activation/deactivation controls.
- **Order management and status updates**: End-to-end lifecycle order tracking (Pending, Confirmed, Shipped, Delivered, Cancelled) with automated invoice generation.
- **Reports and analytics**: Dynamic financial summaries by revenue, date ranges, and sales distribution across catalog categories.
- **Low-stock monitoring**: Real-time automated alerts highlighting inventory items falling below configurable safety thresholds.
- **Email outbox & simulated messaging**: Transparent audit ledger of all transactional emails, registration notifications, and simulated password resets dispatched by the backend.

### Data model
The application stores data for:
- users
- products
- orders
- reviews
- wishlists
- contact messages
- email records

---

## Technology Stack

### Application layer
- Python 3.12
- Flask
- MongoDB
- Jinja2 templates
- HTML5, CSS3, JavaScript
- Gunicorn
- ReportLab for PDF invoice generation

### DevOps and infrastructure layer
- Docker
- Docker Compose
- Jenkins
- Terraform
- Ansible
- Kubernetes manifests
- AWS deployment patterns and infrastructure modules
- Monitoring and observability assets (Prometheus/Grafana references)

---

## Architecture Summary

The repository reflects a layered DevOps architecture for a web application that can be deployed in AWS with Kubernetes-oriented patterns.

A simplified view is:

```text
Browser
  → Flask application container
  → MongoDB database
  → Jenkins / Terraform / Ansible automation pipeline
  → AWS infrastructure and Kubernetes deployment assets
```

Key infrastructure and delivery assets include:
- `Dockerfile`
- `docker-compose.yml`
- `Jenkinsfile`
- `terraform/`
- `ansible/`
- `k8s/`
- `monitoring/`
- `project_artifacts/`

Architecture references and sprint documentation are included in:
- `project_artifacts/Lumora_E-Commerce_Architecture_v3.png`
- `project_artifacts/Capstone_Task_Execution_Roadmap.md`
- `project_artifacts/Project_Sprints.txt`

---

## Repository Structure

```text
hv-ecommerce-devops/
├── app/
│   ├── static/
│   ├── templates/
│   ├── __init__.py
│   └── routes.py
├── ansible/
│   ├── README.md
│   ├── ansible.cfg
│   ├── inventory/
│   ├── playbooks/
│   └── roles/
├── k8s/
│   ├── 00-namespace.yml
│   ├── 01-configmap-secrets.yml
│   ├── 02-mongodb.yml
│   ├── 03-flask-deployment.yml
│   ├── 04-hpa.yml
│   ├── 05-service-ingress.yml
│   └── kustomization.yml
├── monitoring/
│   ├── alertmanager/
│   └── prometheus/
├── project_artifacts/
│   ├── Lumora_E-Commerce_Architecture_v3.png
│   ├── Capstone_Task_Execution_Roadmap.md
│   ├── DevOps_Capstone_Viva_Preparation_Guide.md
│   ├── Implementation_Plan_Sprint2_Jenkins_Automation.md
│   ├── Jenkinsfile
│   ├── Project_Sprints.txt
│   ├── Project4_ProblemStatement.txt
│   └── screenshots/
├── scripts/
│   └── setup_metrics_server.sh
├── terraform/
│   ├── modules/
│   ├── budgets.tf
│   ├── main.tf
│   ├── outputs.tf
│   ├── providers.tf
│   ├── secrets.tf
│   ├── terraform.tfvars
│   ├── variables.tf
│   └── versions.tf
├── tests/
│   ├── conftest.py
│   ├── test_app.py
│   └── test_phase5.py
├── .dockerignore
├── .gitignore
├── Capstone-Sprint1-Issue2-Dockerization.docx
├── Dockerfile
├── Jenkinsfile
├── README.md
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── run.py
└── .git
```

---

## Local Setup

### Prerequisites
- Python 3.12+
- Docker Desktop or Docker Engine
- Docker Compose
- Git

### 1) Clone the repository

```bash
git clone https://github.com/Saranyaharish93/hv-ecommerce-devops.git
cd hv-ecommerce-devops
```

### 2) Create a virtual environment

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Linux/macOS
# source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4) Run the application locally

```bash
python run.py
```

The app will be available at:

```text
http://localhost:5000
```

---

## Running with Docker Compose

The repository includes a local containerized setup for the Flask app and MongoDB.

```bash
docker compose up --build
```

Then open:

```text
http://localhost:5000
```

The Compose configuration orchestrates:
- the Flask application service
- the MongoDB service
- persistent database storage as a Docker volume

---

## Configuration and Environment Variables

The app reads environment values when present.

| Variable | Default | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | `dev-secret-change-me` | Flask session signing |
| `MONGO_URI` | `mongodb://mongo:27017/ecommerce` | MongoDB connection string |
| `LOW_STOCK_THRESHOLD` | `10` | Low-stock detection threshold |
| `ADMIN_EMAIL` | `admin@lumora.local` | Bootstrap admin email |
| `ADMIN_PASSWORD` | `Admin@123` | Bootstrap admin password |

Example:

```bash
export SECRET_KEY='your-secret-key'
export MONGO_URI='mongodb://localhost:27017/ecommerce'
export ADMIN_EMAIL='admin@lumora.local'
export ADMIN_PASSWORD='Admin@123'
```

> The demo admin credentials are intended for local or non-production use only.

---

## Health Check and Core Routes

The application exposes a health endpoint used for deployment readiness and monitoring checks.

```text
GET /health
```

Example URL:

```text
http://localhost:5000/health
```

Core application routes include:
- `/` — home page
- `/shop` — storefront catalog
- `/product/<product_id>` — product detail
- `/cart` — shopping cart
- `/checkout` — checkout flow
- `/orders` — order history
- `/track-order` — order tracking
- `/account` — customer account
- `/admin` — admin dashboard
- `/contact` — contact form
- `/about` — about page

---

## Automated Testing

The project contains automated tests under the `tests/` directory.

Run the suite with:

```bash
pytest -q
```

If dependencies are not already installed:

```bash
pip install -r requirements-dev.txt
pytest -q
```

Current tests cover:
- application health endpoint validation
- seeded product data presence

---

## Docker

The application is containerized using a Python-based Docker image and is designed to run behind Gunicorn.

Build the application image:

```bash
docker build -t lumora-app .
```

Run the application manually:

```bash
docker run -p 5000:5000 --env-file .env lumora-app
```

The Compose setup runs both the Flask application and MongoDB together and keeps the database volume persistent.

---

## DevOps Assets

### Jenkins
The repository contains a battle-tested Jenkins declarative pipeline in `Jenkinsfile`.

Typical pipeline goals include:
- Terraform validation and planning
- AWS CLI and credential verification
- Ansible syntax checks
- Pytest execution
- Docker build and image tagging
- Trivy-based vulnerability scanning
- ECR push steps
- Kubernetes deployment automation

### Terraform
The `terraform/` directory contains infrastructure as code for AWS networking, security groups, ECR, and EKS-related resources.

### Ansible
The `ansible/` directory includes inventory, playbooks, and roles for provisioning Jenkins and related tooling across hosts.

### Kubernetes
The `k8s/` directory includes manifests for:
- namespace setup
- ConfigMaps and secrets
- MongoDB deployment
- Flask app deployment
- HPA configuration
- service and ingress rules

### Monitoring and documentation artifacts
The `project_artifacts/` directory stores architecture diagrams, sprint planning documents, the task execution roadmap, and project notes used for the capstone deliverable.

---

## License

This project is intended for educational and capstone demonstration use.

---

## Summary

Lumora is both a working e-commerce storefront and a realistic DevOps capstone project. It demonstrates how application development, infrastructure provisioning, containerization, automation, and deployment practices can come together in a single repository to model a modern delivery pipeline.
