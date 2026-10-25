# Lumora E-Commerce DevOps: Kubernetes Quick Reference & Operations Cheat Sheet

This operations cheat sheet contains the most frequently used `kubectl` commands tailored directly to the **Lumora E-Commerce** EKS cluster, namespaces (`monitoring`, `lumora-prod`), and services. Use this as an immediate reference during demonstrations, vivas, screenshot captures, and cluster troubleshooting.

---

## Table of Contents

1. [Accessing Web Consoles (Port-Forwarding)](#1-accessing-web-consoles-port-forwarding)
2. [Retrieving Passwords & Secrets](#2-retrieving-passwords--secrets)
3. [Viewing Logs & Troubleshooting Pods](#3-viewing-logs--troubleshooting-pods)
4. [Checking Workload, Pod & Service Health](#4-checking-workload-pod--service-health)
5. [Resource Metrics, HPA & Autoscaling](#5-resource-metrics-hpa--autoscaling)
6. [Interactive Shell & In-Cluster Network Testing](#6-interactive-shell--in-cluster-network-testing)
7. [Deployments, Rollouts & Restarts](#7-deployments-rollouts--restarts)
8. [Storage & Persistent Volume Claims (PVC)](#8-storage--persistent-volume-claims-pvc)

---

## 1. Accessing Web Consoles (Port-Forwarding)

Run these commands in a terminal window to open local browser tunnels to cluster services.

### Grafana Console (Port 3000)
```powershell
# Forward Grafana service to http://localhost:3000
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
```
- **URL**: [http://localhost:3000](http://localhost:3000)
- **User**: `admin`
- **Password**: *(See Section 2 below)*

### Prometheus Console (Port 9090)
```powershell
# Forward Prometheus server to http://localhost:9090
kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090 -n monitoring
```
- **URL**: [http://localhost:9090](http://localhost:9090)
- **Key Pages**:
  - Targets Health: `http://localhost:9090/targets`
  - Active Alerts: `http://localhost:9090/alerts`

### Flask E-Commerce Application (Port 5000)
```powershell
# Bypass ALB and test Flask app directly
kubectl port-forward svc/flask-service 5000:5000 -n lumora-prod
```
- **URL**: [http://localhost:5000](http://localhost:5000)
- **Health Check**: [http://localhost:5000/health](http://localhost:5000/health)
- **Metrics Endpoint**: [http://localhost:5000/metrics](http://localhost:5000/metrics)

---

## 2. Retrieving Passwords & Secrets

### Get Grafana `admin` Password

#### Windows PowerShell:
```powershell
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((kubectl get secret --namespace monitoring prometheus-grafana -o jsonpath="{.data.admin-password}")))
```

#### Linux / macOS / Git Bash:
```bash
kubectl get secret --namespace monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```

### View Application Secrets in `lumora-prod`
```powershell
# List secrets in production namespace
kubectl get secrets -n lumora-prod

# Decode MongoDB URI secret (PowerShell)
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((kubectl get secret app-secrets -n lumora-prod -o jsonpath="{.data.MONGO_URI}")))
```

---

## 3. Viewing Logs & Troubleshooting Pods

### Live Streaming Logs (`-f`)
```powershell
# Follow live logs for the Flask application deployment
kubectl logs -f deployment/flask-app -n lumora-prod --tail=100

# Follow logs from a specific pod
kubectl logs -f <pod-name> -n lumora-prod

# Follow logs of Grafana pod
kubectl logs -f deployment/prometheus-grafana -n monitoring -c grafana
```

### Inspecting Previous Crashed Containers (`-p`)
If a container crashed and restarted (`CrashLoopBackOff`), view why it failed:
```powershell
kubectl logs <pod-name> -n lumora-prod --previous
```

### Inspecting Multi-Container Pods
```powershell
# View logs from a specific container inside a multi-container pod
kubectl logs <pod-name> -n monitoring -c <container-name>
```

### Deep Diagnostics via `describe`
```powershell
# View pod lifecycle events, probe failures, and image pull errors
kubectl describe pod <pod-name> -n lumora-prod

# View cluster-wide recent warning events
kubectl get events -n lumora-prod --sort-by='.metadata.creationTimestamp'
```

---

## 4. Checking Workload, Pod & Service Health

### Overview Across Namespaces
```powershell
# View all pods in all namespaces
kubectl get pods -A

# View wide details (Pod IP, Node assignments)
kubectl get pods -n lumora-prod -o wide

# Check all resources in application namespace
kubectl get all -n lumora-prod

# Check monitoring stack status
kubectl get pods,svc -n monitoring
```

### Inspecting Ingress & AWS Load Balancers
```powershell
# Check ALB Ingress address and status
kubectl get ingress -n lumora-prod

# Detailed routing rules and annotations of ALB
kubectl describe ingress alb-ingress -n lumora-prod
```

---

## 5. Resource Metrics, HPA & Autoscaling

### Node and Pod CPU/Memory Utilization
```powershell
# View CPU and RAM usage of all EKS worker nodes
kubectl top nodes

# View CPU and RAM consumption per pod
kubectl top pods -n lumora-prod

# View monitoring stack resource usage
kubectl top pods -n monitoring
```

### Horizontal Pod Autoscaler (HPA) Status
```powershell
# Check current replicas, targets, and max replicas
kubectl get hpa -n lumora-prod

# Detailed HPA scaling metrics and recent scaling events
kubectl describe hpa flask-hpa -n lumora-prod
```

---

## 6. Interactive Shell & In-Cluster Network Testing

### Exec into a Running Pod
```powershell
# Open interactive bash shell inside Flask container
kubectl exec -it deployment/flask-app -n lumora-prod -- /bin/bash

# Open shell in MongoDB pod
kubectl exec -it mongodb-0 -n lumora-prod -- mongosh
```

### Test Internal DNS & Service Endpoints from Inside Pod
```bash
# Verify internal DNS resolution and MongoDB connectivity
curl -I http://flask-service.lumora-prod.svc.cluster.local:5000/health

# Verify application metrics endpoint
curl -s http://flask-service.lumora-prod.svc.cluster.local:5000/metrics | head -n 25
```

---

## 7. Deployments, Rollouts & Restarts

### Triggering Rolling Restarts
```powershell
# Restart Flask application with zero downtime
kubectl rollout restart deployment/flask-app -n lumora-prod

# Check progress of rollout
kubectl rollout status deployment/flask-app -n lumora-prod

# View rollout history
kubectl rollout history deployment/flask-app -n lumora-prod
```

### Manual Scaling for Stress / Load Testing
```powershell
# Temporarily scale application pods up or down
kubectl scale deployment/flask-app --replicas=5 -n lumora-prod

# Revert back to 2 replicas
kubectl scale deployment/flask-app --replicas=2 -n lumora-prod
```

---

## 8. Storage & Persistent Volume Claims (PVC)

```powershell
# Check PVC bound status for MongoDB database
kubectl get pvc -n lumora-prod

# Check PV storage class and capacity
kubectl get pv

# Describe PVC to diagnose EBS volume attach/mount issues
kubectl describe pvc mongodb-data-mongodb-0 -n lumora-prod
```

---

## Quick Reference Summary Table

| Task | Command |
| :--- | :--- |
| **Open Grafana Console** | `kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring` |
| **Get Grafana Password (PS)** | `[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((kubectl get secret --namespace monitoring prometheus-grafana -o jsonpath="{.data.admin-password}")))` |
| **Open Prometheus Console** | `kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090 -n monitoring` |
| **Open Flask App Locally** | `kubectl port-forward svc/flask-service 5000:5000 -n lumora-prod` |
| **App Live Logs** | `kubectl logs -f deployment/flask-app -n lumora-prod --tail=100` |
| **Previous Crash Logs** | `kubectl logs <pod-name> -n lumora-prod --previous` |
| **Cluster Node CPU/RAM** | `kubectl top nodes` |
| **Pod CPU/RAM** | `kubectl top pods -n lumora-prod` |
| **HPA Status** | `kubectl get hpa -n lumora-prod` |
| **Rolling Restart App** | `kubectl rollout restart deployment/flask-app -n lumora-prod` |
| **Pod Interactive Shell** | `kubectl exec -it deployment/flask-app -n lumora-prod -- /bin/bash` |
