#!/bin/bash
# Kubernetes Troubleshooting Script

echo "=== Checking Pod Status ==="
kubectl get pods -n cancer-mlops

echo ""
echo "=== Checking Pod Events (last pod) ==="
POD_NAME=$(kubectl get pods -n cancer-mlops -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod $POD_NAME -n cancer-mlops | tail -20

echo ""
echo "=== Checking PVC Status ==="
kubectl get pvc -n cancer-mlops

echo ""
echo "=== Checking Storage Classes ==="
kubectl get storageclass

echo ""
echo "=== Checking Nodes ==="
kubectl get nodes

echo ""
echo "=== Checking Events ==="
kubectl get events -n cancer-mlops --sort-by='.lastTimestamp' | tail -10
