# Observability, Monitoring, and Alerting

This document outlines the observability, metrics collection, and alerting architecture designed for the Lumora E-Commerce platform across application, cluster, and infrastructure tiers.

---

## Table of Contents

1. [Observability Strategy and SRE Principles](#1-observability-strategy-and-sre-principles)
2. [Automated Metrics Server Bootstrap with In-Context Verification](#2-automated-metrics-server-bootstrap-with-in-context-verification)
3. [Prometheus Architecture and Scraping Targets with Target Proof](#3-prometheus-architecture-and-scraping-targets-with-target-proof)
4. [Grafana KPI Dashboards with In-Context Visuals](#4-grafana-kpi-dashboards-with-in-context-visuals)
5. [Alertmanager Rules and Notification Routing with Alert Delivery Proof](#5-alertmanager-rules-and-notification-routing-with-alert-delivery-proof)

---

## 1. Observability Strategy and SRE Principles

The monitoring framework follows the Google Site Reliability Engineering (SRE) **Four Golden Signals**:
1. **Latency**: Time required to service client HTTP requests across endpoints (`/`, `/shop`, `/product/<id>`).
2. **Traffic**: Volume of incoming transactions measured in requests per second (RPS).
3. **Errors**: Rate of failed requests, categorized into 4xx (client errors) and 5xx (application / server errors).
4. **Saturation**: Utilization of critical infrastructure resources (Node CPU, Pod Memory vs Limit, EBS Disk IOPS).

---

## 2. Automated Metrics Server Bootstrap with In-Context Verification

Kubernetes Horizontal Pod Autoscaling (HPA) requires an active resource metrics pipeline. We automate this pre-flight check in [scripts/setup_metrics_server.sh](file:///d:/HeroVired/Capstone/Saro/hv-ecommerce-devops/scripts/setup_metrics_server.sh):

```bash
# Verify if Metrics API Service is active
if ! kubectl get apiservice v1beta1.metrics.k8s.io >/dev/null 2>&1; then
    echo "Metrics Server API not detected. Installing official Kubernetes Metrics Server..."
    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
fi

# Wait for healthy rollout
kubectl rollout status deployment/metrics-server -n kube-system --timeout=120s

# Verify active metric reporting
kubectl top nodes
```

This script runs automatically during the Jenkins pipeline Stage 16 prior to deploying application workloads.

> **Screenshot Placement: Kubernetes Metrics Server Verification CLI**  
> *Insert Here*: Terminal output of `kubectl top nodes` and `kubectl top pods -n lumora-prod` demonstrating active CPU and RAM collection.  
> *Target Image File*: `project_artifacts/screenshots/monitoring/01_metrics_server_nodes.png`  
> *Markdown Embed Syntax*: `![Metrics Server Verification](../project_artifacts/screenshots/monitoring/01_metrics_server_nodes.png)`

---

## 3. Prometheus Architecture and Scraping Targets with Target Proof

The monitoring tier uses Prometheus deployed via the official `kube-prometheus-stack` Helm chart. It monitors three distinct operational layers:
- **Application Layer**: Flask `/metrics` endpoint (request durations, status code distributions, and active sessions).
- **Cluster & Pod Layer**: `kube-state-metrics` (deployment health, pod restart counts, and persistent volume statuses).
- **Host & Node Layer**: `node-exporter` (EC2 worker node CPU, memory pressure, and EBS disk I/O).

### Scraping Configurations:
- **Scrape Interval**: 15 seconds across all targets.
- **Evaluation Interval**: 15 seconds for rapid alert detection.
- **ServiceMonitor**: Automatically discovers Flask pods in `lumora-prod` labeled `app: flask-app`.

> **Screenshot Placement: Prometheus Web Console Active Scraping Targets**  
> *Insert Here*: Web browser screenshot of Prometheus (`:9090/targets`) displaying healthy endpoints (`1/1 UP`) across Flask endpoints, node-exporter, and kube-state-metrics.  
> *Target Image File*: `project_artifacts/screenshots/monitoring/02_prometheus_targets_up.png`  
> *Markdown Embed Syntax*: `![Prometheus Active Scraping Targets](../project_artifacts/screenshots/monitoring/02_prometheus_targets_up.png)`

---

## 4. Grafana KPI Dashboards with In-Context Visuals

Grafana visualizes Prometheus metrics through two dedicated dashboards:

### 4.1. Dashboard 1: Application Performance & Business KPIs
- **Throughput Panel**: Real-time HTTP requests per second across `/`, `/shop`, `/checkout`.
- **Response Latency (P50, P95, P99)**: Millisecond duration percentiles to monitor end-user experience.
- **HTTP Error Rate**: Stacked area chart showing ratio of 200 OK vs 500 Internal Server Errors.
- **Database Transaction Latency**: Time spent servicing MongoDB queries via `pymongo`.

> **Screenshot Placement: Grafana Application KPI Dashboard**  
> *Insert Here*: Full Grafana dashboard showing graphs for HTTP throughput (RPS), P95 response latency, order rate, and 4xx/5xx status ratios.  
> *Target Image File*: `project_artifacts/screenshots/monitoring/03_grafana_app_kpi.png`  
> *Markdown Embed Syntax*: `![Grafana Application KPI Dashboard](../project_artifacts/screenshots/monitoring/03_grafana_app_kpi.png)`

### 4.2. Dashboard 2: Kubernetes Infrastructure & Node Saturation
- **Pod CPU & Memory Utilization**: Live consumption charted against pod `requests` and `limits`.
- **HPA Scaling Activity**: Visual correlation between CPU spikes and pod replica expansion.
- **Node Saturation**: Worker node CPU load average and memory pressure.
- **EBS Disk Utilization**: Storage space used on `mongodb-0` 10 GiB EBS volume.

> **Screenshot Placement: Grafana Kubernetes Infrastructure Saturation Dashboard**  
> *Insert Here*: Full Grafana dashboard showing EKS worker node CPU/memory load, pod memory limit consumption, and active HPA pod scaling curves.  
> *Target Image File*: `project_artifacts/screenshots/monitoring/04_grafana_cluster_infra.png`  
> *Markdown Embed Syntax*: `![Grafana Cluster Saturation Dashboard](../project_artifacts/screenshots/monitoring/04_grafana_cluster_infra.png)`

---

## 5. Alertmanager Rules and Notification Routing with Alert Delivery Proof

Alertmanager evaluates metrics continuously and dispatches notifications when thresholds are breached:

```yaml
groups:
  - name: lumora_critical_alerts
    rules:
      - alert: HighHttpErrorRate
        expr: rate(flask_http_request_total{status=~"5.."}[5m]) / rate(flask_http_request_total[5m]) * 100 > 5
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Flask Application High Error Rate"
          description: "HTTP 5xx error rate exceeded 5% over the last 5 minutes."

      - alert: PodCrashLooping
        expr: rate(kube_pod_container_status_restarts_total{namespace="lumora-prod"}[15m]) > 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Container CrashLoop Detected in lumora-prod"
          description: "Pod {{ $labels.pod }} restarted multiple times."

      - alert: NodeMemorySaturation
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "EKS Worker Node Memory Near Exhaustion"
          description: "Worker node memory usage exceeded 85%."
```

### Notification Routing:
- **Slack Integration**: Webhook notification posted to `#lumora-devops-alerts`.
- **Email Notification**: Amazon SNS topic sending alerts to the core engineering team.

> **Screenshot Placement: Alertmanager Notification in Slack / Email Channel**  
> *Insert Here*: Screenshot of an alert card delivered to Slack or email showing alert severity, description, impacted pod name, and trigger timestamp.  
> *Target Image File*: `project_artifacts/screenshots/monitoring/05_alertmanager_notification.png`  
> *Markdown Embed Syntax*: `![Alertmanager Delivered Notification](../project_artifacts/screenshots/monitoring/05_alertmanager_notification.png)`


