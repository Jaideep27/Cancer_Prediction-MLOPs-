#!/bin/bash

# Cancer MLOps Kubernetes Status Check Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="cancer-mlops"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Cancer MLOps Deployment Status${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if namespace exists
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
    echo -e "${RED}Error: Namespace '$NAMESPACE' does not exist${NC}"
    echo -e "${YELLOW}Run deploy.sh to create the deployment${NC}"
    exit 1
fi

echo -e "${GREEN}Namespace:${NC} $NAMESPACE"
echo ""

# Pods Status
echo -e "${YELLOW}=== PODS ===${NC}"
kubectl get pods -n $NAMESPACE -o wide

echo ""
echo -e "${YELLOW}Pod Status Summary:${NC}"
TOTAL_PODS=$(kubectl get pods -n $NAMESPACE --no-headers | wc -l)
RUNNING_PODS=$(kubectl get pods -n $NAMESPACE --no-headers | grep -c "Running" || echo "0")
echo -e "  Total: $TOTAL_PODS"
echo -e "  Running: $RUNNING_PODS"

if [ "$RUNNING_PODS" -eq "$TOTAL_PODS" ] && [ "$TOTAL_PODS" -gt 0 ]; then
    echo -e "  ${GREEN}✓ All pods running${NC}"
else
    echo -e "  ${RED}✗ Some pods not running${NC}"
fi

# Services Status
echo ""
echo -e "${YELLOW}=== SERVICES ===${NC}"
kubectl get svc -n $NAMESPACE

# Check external IPs for LoadBalancer services
echo ""
echo -e "${YELLOW}External Access Points:${NC}"
LB_IP=$(kubectl get svc api-service-external -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
if [ -n "$LB_IP" ]; then
    echo -e "  API LoadBalancer: ${GREEN}http://$LB_IP${NC}"
else
    echo -e "  API LoadBalancer: ${YELLOW}Pending...${NC}"
fi

# PVCs Status
echo ""
echo -e "${YELLOW}=== PERSISTENT VOLUME CLAIMS ===${NC}"
kubectl get pvc -n $NAMESPACE

echo ""
echo -e "${YELLOW}PVC Status Summary:${NC}"
TOTAL_PVCS=$(kubectl get pvc -n $NAMESPACE --no-headers | wc -l)
BOUND_PVCS=$(kubectl get pvc -n $NAMESPACE --no-headers | grep -c "Bound" || echo "0")
echo -e "  Total: $TOTAL_PVCS"
echo -e "  Bound: $BOUND_PVCS"

if [ "$BOUND_PVCS" -eq "$TOTAL_PVCS" ] && [ "$TOTAL_PVCS" -gt 0 ]; then
    echo -e "  ${GREEN}✓ All PVCs bound${NC}"
else
    echo -e "  ${RED}✗ Some PVCs not bound${NC}"
fi

# ConfigMaps
echo ""
echo -e "${YELLOW}=== CONFIGMAPS ===${NC}"
kubectl get configmap -n $NAMESPACE

# Ingress
echo ""
echo -e "${YELLOW}=== INGRESS ===${NC}"
if kubectl get ingress -n $NAMESPACE &> /dev/null; then
    kubectl get ingress -n $NAMESPACE
else
    echo -e "  ${YELLOW}No Ingress resources found${NC}"
fi

# Resource Usage
echo ""
echo -e "${YELLOW}=== RESOURCE USAGE ===${NC}"
kubectl top pods -n $NAMESPACE 2>/dev/null || echo -e "  ${YELLOW}Metrics not available (install metrics-server)${NC}"

# Recent Events
echo ""
echo -e "${YELLOW}=== RECENT EVENTS ===${NC}"
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -10

# Health Checks
echo ""
echo -e "${YELLOW}=== HEALTH CHECKS ===${NC}"

# Check if API is responsive
API_POD=$(kubectl get pods -n $NAMESPACE -l app=cancer-mlops-api -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$API_POD" ]; then
    echo -e "${YELLOW}Checking API health...${NC}"
    kubectl exec -n $NAMESPACE $API_POD -- curl -s http://localhost:8000/health > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "  API: ${GREEN}✓ Healthy${NC}"
    else
        echo -e "  API: ${RED}✗ Unhealthy${NC}"
    fi
else
    echo -e "  API: ${YELLOW}No pod found${NC}"
fi

# Check MLflow
MLFLOW_POD=$(kubectl get pods -n $NAMESPACE -l app=mlflow -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$MLFLOW_POD" ]; then
    echo -e "${YELLOW}Checking MLflow health...${NC}"
    kubectl exec -n $NAMESPACE $MLFLOW_POD -- curl -s http://localhost:5000/health > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "  MLflow: ${GREEN}✓ Healthy${NC}"
    else
        echo -e "  MLflow: ${YELLOW}~ Response received${NC}"
    fi
else
    echo -e "  MLflow: ${YELLOW}No pod found${NC}"
fi

# Check Prometheus
PROM_POD=$(kubectl get pods -n $NAMESPACE -l app=prometheus -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$PROM_POD" ]; then
    echo -e "${YELLOW}Checking Prometheus health...${NC}"
    kubectl exec -n $NAMESPACE $PROM_POD -- curl -s http://localhost:9090/-/healthy > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "  Prometheus: ${GREEN}✓ Healthy${NC}"
    else
        echo -e "  Prometheus: ${RED}✗ Unhealthy${NC}"
    fi
else
    echo -e "  Prometheus: ${YELLOW}No pod found${NC}"
fi

# Check Grafana
GRAFANA_POD=$(kubectl get pods -n $NAMESPACE -l app=grafana -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$GRAFANA_POD" ]; then
    echo -e "${YELLOW}Checking Grafana health...${NC}"
    kubectl exec -n $NAMESPACE $GRAFANA_POD -- curl -s http://localhost:3000/api/health > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "  Grafana: ${GREEN}✓ Healthy${NC}"
    else
        echo -e "  Grafana: ${RED}✗ Unhealthy${NC}"
    fi
else
    echo -e "  Grafana: ${YELLOW}No pod found${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Quick Access Commands${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${YELLOW}Port-forward services:${NC}"
echo "  kubectl port-forward -n $NAMESPACE svc/api-service 8000:8000"
echo "  kubectl port-forward -n $NAMESPACE svc/mlflow-service 5000:5000"
echo "  kubectl port-forward -n $NAMESPACE svc/prometheus-service 9090:9090"
echo "  kubectl port-forward -n $NAMESPACE svc/grafana-service 3000:3000"
echo ""

echo -e "${YELLOW}View logs:${NC}"
echo "  kubectl logs -f deployment/api-deployment -n $NAMESPACE"
echo "  kubectl logs -f deployment/mlflow-deployment -n $NAMESPACE"
echo "  kubectl logs -f deployment/prometheus-deployment -n $NAMESPACE"
echo "  kubectl logs -f deployment/grafana-deployment -n $NAMESPACE"
echo ""

echo -e "${YELLOW}Scale API:${NC}"
echo "  kubectl scale deployment api-deployment -n $NAMESPACE --replicas=5"
echo ""
