#!/bin/bash

# Cancer MLOps Kubernetes Deployment Script
# This script deploys all components to a Kubernetes cluster

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="cancer-mlops"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cancer MLOps Kubernetes Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: Cannot connect to Kubernetes cluster${NC}"
    exit 1
fi

echo -e "${YELLOW}Current cluster:${NC}"
kubectl cluster-info | head -n 1
echo ""

read -p "Deploy to this cluster? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Deployment cancelled${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Step 1: Creating namespace...${NC}"
kubectl apply -f "${SCRIPT_DIR}/namespace.yaml"
sleep 2

echo ""
echo -e "${GREEN}Step 2: Creating ConfigMaps...${NC}"
kubectl apply -f "${SCRIPT_DIR}/configmaps.yaml"
sleep 2

echo ""
echo -e "${GREEN}Step 3: Creating PersistentVolumeClaims...${NC}"
kubectl apply -f "${SCRIPT_DIR}/persistent-volumes.yaml"

echo -e "${YELLOW}Waiting for PVCs to be bound...${NC}"
for pvc in models-pvc data-pvc mlflow-artifacts-pvc mlflow-backend-pvc prometheus-data-pvc grafana-data-pvc logs-pvc; do
    kubectl wait --for=condition=Bound pvc/$pvc -n $NAMESPACE --timeout=120s || {
        echo -e "${RED}Warning: PVC $pvc not bound yet${NC}"
    }
done
sleep 2

echo ""
echo -e "${GREEN}Step 4: Deploying MLflow...${NC}"
kubectl apply -f "${SCRIPT_DIR}/mlflow-deployment.yaml"
sleep 5

echo ""
echo -e "${GREEN}Step 5: Deploying Prometheus...${NC}"
kubectl apply -f "${SCRIPT_DIR}/prometheus-deployment.yaml"
sleep 5

echo ""
echo -e "${GREEN}Step 6: Deploying Grafana...${NC}"
kubectl apply -f "${SCRIPT_DIR}/grafana-deployment.yaml"
sleep 5

echo ""
echo -e "${GREEN}Step 7: Deploying API...${NC}"
kubectl apply -f "${SCRIPT_DIR}/api-deployment.yaml"
sleep 5

echo ""
echo -e "${GREEN}Step 8: Creating Ingress (optional)...${NC}"
read -p "Deploy Ingress? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    kubectl apply -f "${SCRIPT_DIR}/ingress.yaml"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment initiated!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${YELLOW}Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=Ready pod -l app=mlflow -n $NAMESPACE --timeout=300s || echo -e "${RED}MLflow pod not ready yet${NC}"
kubectl wait --for=condition=Ready pod -l app=prometheus -n $NAMESPACE --timeout=300s || echo -e "${RED}Prometheus pod not ready yet${NC}"
kubectl wait --for=condition=Ready pod -l app=grafana -n $NAMESPACE --timeout=300s || echo -e "${RED}Grafana pod not ready yet${NC}"
kubectl wait --for=condition=Ready pod -l app=cancer-mlops-api -n $NAMESPACE --timeout=300s || echo -e "${RED}API pod not ready yet${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Status${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${YELLOW}Pods:${NC}"
kubectl get pods -n $NAMESPACE

echo ""
echo -e "${YELLOW}Services:${NC}"
kubectl get svc -n $NAMESPACE

echo ""
echo -e "${YELLOW}PVCs:${NC}"
kubectl get pvc -n $NAMESPACE

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Access Information${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${YELLOW}To access services via port-forward:${NC}"
echo ""
echo "  API:"
echo "    kubectl port-forward -n $NAMESPACE svc/api-service 8000:8000"
echo "    URL: http://localhost:8000"
echo ""
echo "  MLflow:"
echo "    kubectl port-forward -n $NAMESPACE svc/mlflow-service 5000:5000"
echo "    URL: http://localhost:5000"
echo ""
echo "  Prometheus:"
echo "    kubectl port-forward -n $NAMESPACE svc/prometheus-service 9090:9090"
echo "    URL: http://localhost:9090"
echo ""
echo "  Grafana:"
echo "    kubectl port-forward -n $NAMESPACE svc/grafana-service 3000:3000"
echo "    URL: http://localhost:3000"
echo "    Credentials: admin/admin"
echo ""

echo -e "${YELLOW}To check logs:${NC}"
echo "  kubectl logs -f deployment/api-deployment -n $NAMESPACE"
echo ""

echo -e "${GREEN}Deployment complete!${NC}"
