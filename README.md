# HV E-Commerce End-to-End DevOps Capstone

A small but complete Python Flask + MongoDB e-commerce application prepared for Docker, Kubernetes, Jenkins, Terraform, Ansible, Trivy, Prometheus and Grafana.

## Features
- Product catalogue
- Session-based shopping cart
- Checkout and order storage in MongoDB
- Health endpoint for Kubernetes probes
- Automated tests
- Docker and Docker Compose
- Kubernetes Deployment, Service, StatefulSet and HPA
- Jenkins CI/CD pipeline
- Terraform AWS VPC + EKS starter infrastructure
- Ansible Jenkins-server setup
- GitHub Actions CI alternative

## Run locally
```bash
cp .env.example .env
docker compose up --build
```
Open `http://localhost:5000`.

## Run tests
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements-dev.txt
pytest -q
```

## Kubernetes quick deployment
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/mongo.yaml
sed 's|IMAGE_PLACEHOLDER|YOUR_DOCKERHUB_USER/hv-ecommerce:1.0.0|g' k8s/app.yaml | kubectl apply -f -
kubectl apply -f k8s/hpa.yaml
kubectl get all -n hv-ecommerce
```

## Suggested one-month plan
- Week 1: application, MongoDB, tests, Git repository
- Week 2: Docker, Docker Compose, image scanning and Jenkins
- Week 3: Terraform EKS, Ansible and Kubernetes deployment
- Week 4: Prometheus/Grafana, alerts, documentation, screenshots and viva preparation

## Important production improvements
Use managed MongoDB such as MongoDB Atlas, store secrets in AWS Secrets Manager, configure HTTPS/Ingress, add authentication, add payment simulation, use ECR rather than Docker Hub, and configure remote Terraform state in S3 with DynamoDB locking.

## Enhanced Lumora UI pages

The application now includes a creative responsive storefront theme and these pages:

- `/` — visual home page
- `/shop` — searchable and filterable product catalogue
- `/product/<id>` — product detail page
- `/categories` — collection gallery
- `/cart` — editable cart and checkout
- `/track-order` — MongoDB-backed order lookup
- `/about` — brand story
- `/contact` — contact form stored in MongoDB

Theme files are located at:

- `app/static/css/style.css`
- `app/static/js/main.js`
- `app/templates/`


## Authentication and admin
Customer users can register at `/register`. Demo administrator credentials are:

- Email: `admin@lumora.local`
- Password: `Admin@123`

Override these with `ADMIN_EMAIL` and `ADMIN_PASSWORD` environment variables before first startup.

## Phase 2 merged features
- Edit customer profile (`/account/edit`)
- Full customer order list and detailed product view
- Order-status timeline
- Cancel orders while Confirmed or Packed, with inventory restoration
- Buy Again to place previous products back into the cart
- Existing authentication, About page, admin dashboard, Docker, Kubernetes, Terraform, Ansible and monitoring files are retained


## Phase 3 merged features

This package includes every feature from Phase 1 and Phase 2 plus:

- Admin product catalogue list and search
- Add, edit and delete product
- Product price, stock, category, rating, badge and image management
- Admin customer search and list
- Customer profile and complete order history view
- Activate or deactivate customer accounts
- Inactive-user login protection

Admin pages:

- `/admin/products`
- `/admin/products/new`
- `/admin/customers`

Default local admin: `admin@lumora.local` / `Admin@123`. Change these with environment variables for non-demo deployments.

## Phase 4 merged features

This package includes every previous phase plus:

- Customer wishlist with save, remove and move-to-bag actions
- Dedicated secure checkout page
- Saved delivery details from the customer profile
- Cash on delivery, UPI demo and card demo payment choices
- Payment method and payment status stored with every order
- Estimated delivery date
- Downloadable PDF invoice from the order-details page
- Updated order details with full address, payment and invoice controls

Customer pages:

- `/wishlist`
- `/checkout`
- `/orders/<order_id>/invoice`

The payment options are demonstrations only and do not process real money.


## Phase 5 merged features
- Forgot-password and time-limited reset tokens (simulated email)
- Admin product image file upload to `app/static/uploads`
- Revenue trend chart and analytics dashboard
- Sales reports by product and category
- Configurable low-stock alerts (`LOW_STOCK_THRESHOLD`)
- Verified-purchase customer reviews and recalculated ratings
- Simulated order-confirmation email outbox and `logs/order_emails.log`
- Additional unit/integration tests in `tests/test_phase5.py`

Demo email messages are intentionally simulated; no real SMTP credentials are required.
