# Kubernetes Workload Manifests

This directory contains the declarative Kubernetes manifests and Kustomize overlays that define the desired state of the Lumora E-Commerce workloads on Amazon EKS. **Argo CD** continuously reconciles this path from GitHub `main` into namespace `lumora-prod` (see [`argocd/application.yaml`](../argocd/application.yaml)).

> **Deep-Dive Technical Guide**: For complete microservices specifications, persistent volume claims, HPA autoscaling, and zero-downtime rolling updates, see the [Kubernetes Orchestration Guide](../devops/kubernetes.md) and [DevOps Platform Master Guide](../devops/README.md).

![GitOps Platform Architecture](../project_artifacts/Lumora_E-Commerce_GitOps_Platform_v4.jpg)

---

## Manifest Directory Structure

```
k8s/
├── 00-namespace.yml           # Defines isolated 'lumora-prod' namespace
├── 01-configmap-secrets.yml   # ConfigMap, IRSA ServiceAccount lumora-app, SecretProviderClass
├── 02-mongodb.yml             # Headless Service + StatefulSet with 10Gi EBS gp3 PVC
├── 03-flask-deployment.yml     # Flask web deployment (RollingUpdate, non-root user, CSI mount)
├── 04-hpa.yml                 # HorizontalPodAutoscaler (2-5 replicas, 70% CPU, 80% RAM)
├── 05-service-ingress.yml     # Internal ClusterIP Service and AWS ALB Ingress (IP target-type)
├── 06-flask-servicemonitor.yml# Prometheus Operator ServiceMonitor (applied outside this Kustomize set)
└── kustomization.yml          # Resources + images.newTag (GitOps image pin)
```

---

## Architectural Highlights

1. **GitOps Source of Truth**: Jenkins commits `images.newTag` after each ECR push; Argo CD syncs this directory (auto prune + self-heal).
2. **Namespace Isolation**: Storefront workloads run in `lumora-prod`; Argo CD itself runs in `argocd`.
3. **Stateless Tier (Flask Application)**:
   - ServiceAccount `lumora-app` (IRSA) for Secrets Store CSI.
   - Zero-downtime rolling updates (`maxSurge: 1`, `maxUnavailable: 0`).
   - Resource requests (`100m CPU / 128Mi RAM`) and limits (`500m CPU / 512Mi RAM`).
   - Decoupled health probes: `/health` (liveness) and `/health/ready` (MongoDB connectivity).
4. **Stateful Tier (MongoDB)**:
   - Single-instance `StatefulSet` (`mongodb-0`) with headless service (`clusterIP: None`).
   - 10 GiB Amazon EBS `gp3` (`storageClassName: gp3`) via the AWS EBS CSI driver.
5. **Networking & Ingress**:
   - `flask-service` as `ClusterIP`; ALB Ingress uses `target-type: ip`.
6. **Zero-Plaintext Secret Injection**:
   - AWS Secrets Store CSI mounts secrets from Secrets Manager; synced into `flask-secrets`.

---

## Deployment Instructions

**Production path (GitOps):** commit/push changes under `k8s/` (or let Jenkins update `newTag`) → Argo CD Application `lumora-prod` syncs automatically.

**Local / emergency apply:**

```bash
# Preview rendered manifests (includes pinned image tag)
kubectl kustomize k8s/

# Apply all manifests via Kustomize (bypass Argo CD only when needed)
kubectl apply -k k8s/

# Verify rollout status
kubectl rollout status deployment/flask-app -n lumora-prod --timeout=180s

# Verify running workloads
kubectl get all,hpa,pvc -n lumora-prod
```

---

## Related Documentation
- [Argo CD Application](../argocd/application.yaml)
- [Kubernetes Workloads & EKS Architecture](../devops/kubernetes.md)
- [Observability, Prometheus & Grafana](../devops/monitoring.md)
- [DevOps Platform Architecture Guide](../devops/README.md)

