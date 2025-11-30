#!/bin/bash

# Cancer MLOps Kubernetes Cleanup Script
# This script removes all deployed components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="cancer-mlops"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${RED}========================================${NC}"
echo -e "${RED}Cancer MLOps Kubernetes Cleanup${NC}"
echo -e "${RED}========================================${NC}"
echo ""

# Check if namespace exists
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
    echo -e "${YELLOW}Namespace '$NAMESPACE' does not exist. Nothing to clean up.${NC}"
    exit 0
fi

echo -e "${YELLOW}This will delete ALL resources in namespace: $NAMESPACE${NC}"
echo -e "${YELLOW}Including:${NC}"
echo "  - All pods and deployments"
echo "  - All services"
echo "  - All persistent volume claims (DATA WILL BE LOST)"
echo "  - All config maps"
echo "  - The namespace itself"
echo ""

read -p "Are you sure you want to continue? (yes/no) " -r
echo
if [[ ! $REPLY == "yes" ]]; then
    echo -e "${GREEN}Cleanup cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}Deleting resources...${NC}"
echo ""

# Delete in reverse order of creation
echo -e "${YELLOW}Step 1: Deleting Ingress...${NC}"
kubectl delete -f "${SCRIPT_DIR}/ingress.yaml" --ignore-not-found=true
sleep 2

echo -e "${YELLOW}Step 2: Deleting API deployment...${NC}"
kubectl delete -f "${SCRIPT_DIR}/api-deployment.yaml" --ignore-not-found=true
sleep 2

echo -e "${YELLOW}Step 3: Deleting Grafana deployment...${NC}"
kubectl delete -f "${SCRIPT_DIR}/grafana-deployment.yaml" --ignore-not-found=true
sleep 2

echo -e "${YELLOW}Step 4: Deleting Prometheus deployment...${NC}"
kubectl delete -f "${SCRIPT_DIR}/prometheus-deployment.yaml" --ignore-not-found=true
sleep 2

echo -e "${YELLOW}Step 5: Deleting MLflow deployment...${NC}"
kubectl delete -f "${SCRIPT_DIR}/mlflow-deployment.yaml" --ignore-not-found=true
sleep 2

echo ""
read -p "Delete PersistentVolumeClaims (this will DELETE ALL DATA)? (yes/no) " -r
echo
if [[ $REPLY == "yes" ]]; then
    echo -e "${YELLOW}Step 6: Deleting PersistentVolumeClaims...${NC}"
    kubectl delete -f "${SCRIPT_DIR}/persistent-volumes.yaml" --ignore-not-found=true
    sleep 2
else
    echo -e "${GREEN}Keeping PersistentVolumeClaims${NC}"
fi

echo -e "${YELLOW}Step 7: Deleting ConfigMaps...${NC}"
kubectl delete -f "${SCRIPT_DIR}/configmaps.yaml" --ignore-not-found=true
sleep 2

echo ""
read -p "Delete namespace '$NAMESPACE'? (yes/no) " -r
echo
if [[ $REPLY == "yes" ]]; then
    echo -e "${YELLOW}Step 8: Deleting namespace...${NC}"
    kubectl delete -f "${SCRIPT_DIR}/namespace.yaml" --ignore-not-found=true
    echo -e "${GREEN}Namespace deleted${NC}"
else
    echo -e "${GREEN}Keeping namespace${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cleanup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if any resources remain
if kubectl get namespace $NAMESPACE &> /dev/null; then
    echo -e "${YELLOW}Remaining resources in namespace:${NC}"
    kubectl get all -n $NAMESPACE
else
    echo -e "${GREEN}All resources deleted${NC}"
fi
