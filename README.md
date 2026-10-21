# Lumora E-Commerce DevOps Capstone

Lumora is a full-stack e-commerce web application built with Python, Flask, and MongoDB. The repository combines a working storefront with the DevOps assets required for an end-to-end capstone project covering CI/CD, cloud infrastructure automation, Docker, Jenkins, Terraform, Ansible, Kubernetes, and observability.

This project is designed to demonstrate a realistic engineering lifecycle: build a functional online store, containerize the application, automate validation and security checks, provision cloud infrastructure, and deploy to a Kubernetes-based environment.

---

## Project Overview

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

## Application Features

### Customer-facing features
- User registration and login
- Session-based authentication and role-aware access
- Password reset flow with simulated email tracking
- Product catalog and browsing
- Product detail pages with ratings and review capability
- Wishlist support
- Shopping cart management
- Checkout flow with demo payment methods
- Order history and recent order browsing
- Individual order detail view
- Order tracking and status lifecycle
- Invoice download
- Contact form
- About page and brand experience
- Responsive storefront UI

### Admin features
- Admin dashboard with key metrics
- Product management: add, edit, delete, price and stock updates
- Image upload support for product listings
- Customer management and activation toggling
- Order management and status updates
- Reports and analytics by revenue and category
- Low-stock monitoring using a configurable threshold
- Email outbox and simulated messaging records

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
- `azure-pipelines.yml`
- `terraform/`
- `ansible/`
- `k8s/`
- `project_artifacts/`

Architecture references and sprint documentation are included in:
- `project_artifacts/architecture_diagram_v2.png`
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
├── project_artifacts/
│   ├── architecture_diagram_v2.png
│   ├── Capstone_Task_Execution_Roadmap.md
│   ├── Implementation_Plan_Sprint2_Jenkins_Automation.md
│   ├── Jenkinsfile
│   ├── Project_Sprints.txt
│   ├── Project4_ProblemStatement.txt
│   └── ...
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
├── README-new.md
├── azure-pipelines.yml
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
The repository contains a Jenkins declarative pipeline in `Jenkinsfile`, along with a sample Azure Pipelines configuration in `azure-pipelines.yml`.

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

## Capstone Roadmap Status

This repository follows a staged DevOps capstone roadmap covering the key phases of the project lifecycle.

### Implemented / complete
- Flask storefront application
- MongoDB integration
- Dockerization
- Docker Compose orchestration
- Automated tests
- Terraform scaffolding and infrastructure modules
- Kubernetes manifests
- Jenkins pipeline templates
- Architecture and sprint documentation

### In progress / planned
- Full AWS deployment execution
- End-to-end Jenkins validation
- Production-level EKS checks
- Prometheus and Grafana setup
- Alerting and incident notification flow
- Final presentation and documentation delivery

See the planning documents here:
- `project_artifacts/Capstone_Task_Execution_Roadmap.md`
- `project_artifacts/Project_Sprints.txt`

---

## Demo Admin Account

For local demonstration, the application creates an admin user automatically if it does not already exist.

Default values:

```text
ADMIN_EMAIL=admin@lumora.local
ADMIN_PASSWORD=Admin@123
```

These credentials are intended for local testing only and should not be used in production environments.

---

## Contributing

- Create feature branches for new work
- Keep application changes and infrastructure assets aligned
- Validate changes locally before merging
- Prefer small, well-documented PRs
- Use the project artifact directory for architecture and sprint records

---

## License

This project is intended for educational and capstone demonstration use.

---

## Summary

Lumora is both a working e-commerce storefront and a realistic DevOps capstone project. It demonstrates how application development, infrastructure provisioning, containerization, automation, and deployment practices can come together in a single repository to model a modern delivery pipeline.