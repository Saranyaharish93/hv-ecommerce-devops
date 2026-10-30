# Kubernetes Workload Manifests

This directory contains the declarative Kubernetes manifests and Kustomize overlays used to deploy and scale the Lumora E-Commerce application on Amazon Elastic Kubernetes Service (EKS).

> **Deep-Dive Technical Guide**: For complete microservices specifications, persistent volume claims, HPA autoscaling, and zero-downtime rolling updates, see the [Kubernetes Orchestration Guide](../devops/kubernetes.md) and [DevOps Platform Master Guide](../devops/README.md).

---

## Manifest Directory Structure

```
k8s/
├── 00-namespace.yml           # Defines isolated 'lumora-prod' namespace
├── 01-configmap-secrets.yml   # Runtime config and AWS Secrets Store CSI SecretProviderClass
├── 02-mongodb.yml             # Headless Service + single-node StatefulSet with 10Gi EBS PVC
├── 03-flask-deployment.yml     # Flask web deployment (RollingUpdate, non-root user, CSI mount)
├── 04-hpa.yml                 # HorizontalPodAutoscaler (2-5 replicas, 70% CPU, 80% RAM)
├── 05-service-ingress.yml     # Internal ClusterIP Service and AWS ALB Ingress (IP target-type)
├── 06-flask-servicemonitor.yml# Prometheus Operator ServiceMonitor for /metrics endpoint
└── kustomization.yml          # Kustomize manifest orchestrating declarative deployment order
```

---

## Architectural Highlights

1. **Namespace Isolation**: All workloads run in the dedicated `lumora-prod` namespace.
2. **Stateless Tier (Flask Application)**:
   - Non-root execution (`appuser`, UID 1000).
   - Zero-downtime rolling updates (`maxSurge: 1`, `maxUnavailable: 0`).
   - Resource requests (`100m CPU / 128Mi RAM`) and limits (`500m CPU / 512Mi RAM`).
   - Decoupled health probes: `/health/live` (process responsiveness) and `/health/ready` (MongoDB connectivity).
3. **Stateful Tier (MongoDB)**:
   - Single-instance `StatefulSet` (`mongodb-0`) with headless service (`clusterIP: None`).
   - 10 GiB Amazon EBS `gp3` persistent volume via the AWS EBS CSI driver.
4. **Networking & Ingress**:
   - `flask-service` configured as `ClusterIP` to avoid creating unnecessary redundant AWS load balancers.
   - AWS Application Load Balancer (ALB) Ingress Controller routes traffic directly to Pod IPs (`target-type: ip`).
5. **Zero-Plaintext Secret Injection**:
   - AWS Secrets Store CSI driver dynamically synchronizes database passwords and session secret keys directly from AWS Secrets Manager into memory volumes.

---

## Deployment Instructions

```bash
# Apply all manifests via Kustomize
kubectl apply -k k8s/

# Verify rollout status
kubectl rollout status deployment/flask-app -n lumora-prod --timeout=180s

# Verify running workloads
kubectl get all,hpa,pvc -n lumora-prod
```

---

## Related Documentation
- [Kubernetes Workloads & EKS Architecture](../devops/kubernetes.md)
- [Observability, Prometheus & Grafana](../devops/monitoring.md)
- [DevOps Platform Architecture Guide](../devops/README.md)

