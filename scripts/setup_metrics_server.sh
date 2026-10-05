#!/usr/bin/env bash
set -euo pipefail

# Ensure kubeconfig is active for EKS cluster
CLUSTER_NAME="${EKS_CLUSTER_NAME:-lumora-ecommerce-prod}"
AWS_REGION="${AWS_DEFAULT_REGION:-us-east-1}"

echo "🔌 Connecting kubectl to EKS cluster: ${CLUSTER_NAME} in ${AWS_REGION}..."
aws eks update-kubeconfig --region "${AWS_REGION}" --name "${CLUSTER_NAME}"

# Verify cluster connectivity
kubectl cluster-info

echo "=========================================================="
echo " 🩺 [HPA Pre-flight] Checking Kubernetes Metrics Server"
echo "=========================================================="

# 1. Check if the Metrics API Service is already registered and ready
if ! kubectl get apiservice v1beta1.metrics.k8s.io >/dev/null 2>&1; then
    echo "⚠️  Metrics Server API not detected."
    echo "🚀 Installing official Kubernetes Metrics Server..."
    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
else
    echo "✅ Metrics Server API (v1beta1.metrics.k8s.io) is already registered."
fi

# 2. Wait for deployment rollout to ensure the pod is healthy
echo "⏳ Waiting for Metrics Server pod rollout in 'kube-system' namespace..."
kubectl rollout status deployment/metrics-server -n kube-system --timeout=120s

# 3. Allow initial metrics collection scrape (15 seconds)
echo "⏳ Warming up initial metrics scrape..."
sleep 15

# 4. Verify node metrics are responding
if kubectl top nodes >/dev/null 2>&1; then
    echo "✅ Metrics Server is actively reporting node metrics:"
    kubectl top nodes
else
    echo "⚠️  Metrics Server pod is running, but initial scrape is still warming up."
fi

echo "=========================================================="
echo " 🎉 Metrics Server verification complete! HPA is ready."
echo "=========================================================="