# Observability, Monitoring & Alerting

This directory contains the Helm values, Prometheus alerting rules, and Grafana dashboard models for the Lumora E-Commerce platform.

> **Deep-Dive Technical Guide**: For complete SRE Four Golden Signals specifications, Prometheus scraping architecture, alert definitions, and dashboard panels, see the [Monitoring & Observability Guide](../devops/monitoring.md) and [DevOps Platform Master Guide](../devops/README.md).

![End-to-End Architecture (Observability column)](../project_artifacts/Lumora_E-Commerce_Architecture_v4.jpg)

Storefront CD is GitOps via Argo CD; this directory remains the home for Prometheus/Grafana values, dashboards, and `application-alerts.yaml` (ServiceMonitor stays in `monitoring` namespace, outside the `lumora-prod` Kustomize set).

---

## Directory Structure

```
monitoring/
├── prometheus-values.yaml                  # kube-prometheus-stack Helm values (scrape intervals, storage retention)
├── grafana-values.yaml                     # Standalone Grafana Helm values (5Gi EBS PVC persistence, resource limits)
├── application-alerts.yaml                 # PrometheusRule custom resource defining operational alerts
├── test-alert.yaml                         # Synthetic alert rule for Alertmanager integration testing
├── grafana-application-dashboard.json      # JSON dashboard: HTTP RPS, P95 latency, 2xx/5xx status codes, sales
└── grafana-infrastructure-dashboard.json   # JSON dashboard: EKS node CPU/RAM, pod limits, EBS IOPS, HPA curves
```

---

## Architectural Highlights

1. **Decoupled Architecture**:
   - `prometheus-values.yaml` disables bundled Grafana (`grafana.enabled: false`) to keep Prometheus lightweight.
   - `grafana-values.yaml` deploys Grafana independently with dedicated 5 GiB Amazon EBS persistent volume storage for dashboards and user state.
2. **Alerting as Code (`application-alerts.yaml`)**:
   - `EKSNodeHighCPU`: Warns when node CPU exceeds 80% for 5m.
   - `EKSNodeHighMemory`: Warns when node RAM exceeds 85% for 5m.
   - `FlaskPodNotReady`: Critical alert when Flask pod remains unready for 2m.
   - `FlaskFrequentRestarts`: Warns when container `flask-app` restarts > 3 times in 15m.
   - `FlaskApplicationDown`: Critical alert when the `/metrics` endpoint is unreachable for 2m.
   - `FlaskDeploymentUnhealthy`: Critical alert when available replicas are below desired count for 3m.
3. **Application Metrics Instrumentation**:
   - Flask exports Prometheus metrics at `/metrics` scraped by Prometheus via `k8s/06-flask-servicemonitor.yml`.

---

## Deployment & Verification

```bash
# Apply Prometheus alerting rules
kubectl apply -f monitoring/application-alerts.yaml

# Verify rules loaded in monitoring namespace
kubectl get prometheusrule lumora-application-alerts -n monitoring

# Verify active scraping targets in Prometheus
kubectl exec -n lumora-prod deployment/flask-app -c flask-app -- python -c "
import urllib.request
with urllib.request.urlopen('http://localhost:5000/metrics', timeout=10) as res:
    assert res.getcode() == 200
    print('Flask metrics endpoint: OK')
"
```

---

## Related Documentation
- [Observability, Prometheus, Grafana & Metrics Server](../devops/monitoring.md)
- [Kubernetes Workloads & EKS Architecture](../devops/kubernetes.md)
- [DevOps Platform Architecture Guide](../devops/README.md)

