#!/bin/bash

# Cancer MLOps Kubernetes Update Script
# This script updates deployments with new images or configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="cancer-mlops"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Cancer MLOps Kubernetes Update${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if namespace exists
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
    echo -e "${RED}Error: Namespace '$NAMESPACE' does not exist${NC}"
    echo -e "${YELLOW}Run deploy.sh first${NC}"
    exit 1
fi

show_menu() {
    echo -e "${YELLOW}What would you like to update?${NC}"
    echo "1) Update API deployment (new image)"
    echo "2) Update all deployments"
    echo "3) Update ConfigMaps"
    echo "4) Update Ingress"
    echo "5) Restart API pods"
    echo "6) Restart all pods"
    echo "7) Scale API replicas"
    echo "8) Exit"
    echo ""
}

update_api_image() {
    echo -e "${YELLOW}Enter new image tag (e.g., cancer-mlops-api:v1.2.0):${NC}"
    read IMAGE_TAG

    if [ -z "$IMAGE_TAG" ]; then
        echo -e "${RED}Error: Image tag cannot be empty${NC}"
        return
    fi

    echo -e "${GREEN}Updating API deployment with image: $IMAGE_TAG${NC}"
    kubectl set image deployment/api-deployment api=$IMAGE_TAG -n $NAMESPACE

    echo -e "${YELLOW}Waiting for rollout to complete...${NC}"
    kubectl rollout status deployment/api-deployment -n $NAMESPACE

    echo -e "${GREEN}API deployment updated successfully${NC}"
}

update_all_deployments() {
    echo -e "${GREEN}Updating all deployments...${NC}"

    kubectl apply -f "${SCRIPT_DIR}/api-deployment.yaml"
    kubectl apply -f "${SCRIPT_DIR}/mlflow-deployment.yaml"
    kubectl apply -f "${SCRIPT_DIR}/prometheus-deployment.yaml"
    kubectl apply -f "${SCRIPT_DIR}/grafana-deployment.yaml"

    echo -e "${YELLOW}Waiting for rollouts to complete...${NC}"
    kubectl rollout status deployment/api-deployment -n $NAMESPACE
    kubectl rollout status deployment/mlflow-deployment -n $NAMESPACE
    kubectl rollout status deployment/prometheus-deployment -n $NAMESPACE
    kubectl rollout status deployment/grafana-deployment -n $NAMESPACE

    echo -e "${GREEN}All deployments updated successfully${NC}"
}

update_configmaps() {
    echo -e "${GREEN}Updating ConfigMaps...${NC}"
    kubectl apply -f "${SCRIPT_DIR}/configmaps.yaml"

    echo -e "${YELLOW}Restarting deployments to pick up new configs...${NC}"
    kubectl rollout restart deployment/api-deployment -n $NAMESPACE
    kubectl rollout restart deployment/mlflow-deployment -n $NAMESPACE
    kubectl rollout restart deployment/prometheus-deployment -n $NAMESPACE
    kubectl rollout restart deployment/grafana-deployment -n $NAMESPACE

    echo -e "${GREEN}ConfigMaps updated and deployments restarted${NC}"
}

update_ingress() {
    echo -e "${GREEN}Updating Ingress...${NC}"
    kubectl apply -f "${SCRIPT_DIR}/ingress.yaml"
    echo -e "${GREEN}Ingress updated successfully${NC}"
}

restart_api() {
    echo -e "${GREEN}Restarting API pods...${NC}"
    kubectl rollout restart deployment/api-deployment -n $NAMESPACE
    kubectl rollout status deployment/api-deployment -n $NAMESPACE
    echo -e "${GREEN}API pods restarted successfully${NC}"
}

restart_all() {
    echo -e "${GREEN}Restarting all pods...${NC}"
    kubectl rollout restart deployment/api-deployment -n $NAMESPACE
    kubectl rollout restart deployment/mlflow-deployment -n $NAMESPACE
    kubectl rollout restart deployment/prometheus-deployment -n $NAMESPACE
    kubectl rollout restart deployment/grafana-deployment -n $NAMESPACE

    echo -e "${YELLOW}Waiting for rollouts to complete...${NC}"
    kubectl rollout status deployment/api-deployment -n $NAMESPACE
    kubectl rollout status deployment/mlflow-deployment -n $NAMESPACE
    kubectl rollout status deployment/prometheus-deployment -n $NAMESPACE
    kubectl rollout status deployment/grafana-deployment -n $NAMESPACE

    echo -e "${GREEN}All pods restarted successfully${NC}"
}

scale_api() {
    echo -e "${YELLOW}Current API replicas:${NC}"
    kubectl get deployment api-deployment -n $NAMESPACE -o jsonpath='{.spec.replicas}'
    echo ""

    echo -e "${YELLOW}Enter number of replicas:${NC}"
    read REPLICAS

    if ! [[ "$REPLICAS" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}Error: Please enter a valid number${NC}"
        return
    fi

    echo -e "${GREEN}Scaling API to $REPLICAS replicas...${NC}"
    kubectl scale deployment api-deployment -n $NAMESPACE --replicas=$REPLICAS

    echo -e "${YELLOW}Waiting for scaling to complete...${NC}"
    kubectl rollout status deployment/api-deployment -n $NAMESPACE

    echo -e "${GREEN}API scaled successfully${NC}"
}

# Main loop
while true; do
    show_menu
    read -p "Enter choice [1-8]: " choice
    echo ""

    case $choice in
        1)
            update_api_image
            ;;
        2)
            update_all_deployments
            ;;
        3)
            update_configmaps
            ;;
        4)
            update_ingress
            ;;
        5)
            restart_api
            ;;
        6)
            restart_all
            ;;
        7)
            scale_api
            ;;
        8)
            echo -e "${GREEN}Exiting...${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please try again.${NC}"
            ;;
    esac

    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo ""
done
