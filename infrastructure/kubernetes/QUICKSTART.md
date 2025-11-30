# Kubernetes Quick Start Guide

Get the Cancer MLOps platform running on Kubernetes in 5 minutes!

## Prerequisites

✓ Kubernetes cluster (minikube, kind, GKE, EKS, AKS, etc.)
✓ kubectl configured
✓ 8GB+ RAM available
✓ 50GB+ storage available

## Option 1: One-Command Deploy (Fastest)

```bash
kubectl apply -f all-in-one.yaml
```

Wait 2-3 minutes for all pods to start, then:

```bash
kubectl get pods -n cancer-mlops --watch
```

## Option 2: Using Helper Script

```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

The script will:
- Create namespace
- Setup ConfigMaps
- Create storage volumes
- Deploy all 4 services
- Wait for pods to be ready
- Show access instructions

## Option 3: Step-by-Step

```bash
# 1. Namespace & Config (10 seconds)
kubectl apply -f namespace.yaml
kubectl apply -f configmaps.yaml

# 2. Storage (30 seconds)
kubectl apply -f persistent-volumes.yaml

# Wait for volumes
kubectl get pvc -n cancer-mlops --watch

# 3. Deploy Services (2 minutes)
kubectl apply -f mlflow-deployment.yaml
kubectl apply -f prometheus-deployment.yaml
kubectl apply -f grafana-deployment.yaml
kubectl apply -f api-deployment.yaml

# Wait for pods
kubectl get pods -n cancer-mlops --watch
```

## Accessing Services

### Quick Access (Port-Forward)

Open 4 terminals and run:

```bash
# Terminal 1 - API
kubectl port-forward -n cancer-mlops svc/api-service 8000:8000

# Terminal 2 - MLflow
kubectl port-forward -n cancer-mlops svc/mlflow-service 5000:5000

# Terminal 3 - Prometheus
kubectl port-forward -n cancer-mlops svc/prometheus-service 9090:9090

# Terminal 4 - Grafana
kubectl port-forward -n cancer-mlops svc/grafana-service 3000:3000
```

Then visit:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MLflow**: http://localhost:5000
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## Testing

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_name": "hybrid_ensemble",
  "model_version": "latest"
}
```

### Make a Prediction

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "radius_mean": 17.99,
      "texture_mean": 10.38,
      "perimeter_mean": 122.8,
      "area_mean": 1001.0,
      "smoothness_mean": 0.1184,
      "compactness_mean": 0.2776,
      "concavity_mean": 0.3001,
      "concave_points_mean": 0.1471,
      "symmetry_mean": 0.2419,
      "fractal_dimension_mean": 0.07871,
      "radius_se": 1.095,
      "texture_se": 0.9053,
      "perimeter_se": 8.589,
      "area_se": 153.4,
      "smoothness_se": 0.006399,
      "compactness_se": 0.04904,
      "concavity_se": 0.05373,
      "concave_points_se": 0.01587,
      "symmetry_se": 0.03003,
      "fractal_dimension_se": 0.006193,
      "radius_worst": 25.38,
      "texture_worst": 17.33,
      "perimeter_worst": 184.6,
      "area_worst": 2019.0,
      "smoothness_worst": 0.1622,
      "compactness_worst": 0.6656,
      "concavity_worst": 0.7119,
      "concave_points_worst": 0.2654,
      "symmetry_worst": 0.4601,
      "fractal_dimension_worst": 0.1189
    }
  }'
```

## Management

### Check Status

```bash
./status.sh
```

### Scale API

```bash
kubectl scale deployment api-deployment -n cancer-mlops --replicas=5
```

### View Logs

```bash
# API logs
kubectl logs -f deployment/api-deployment -n cancer-mlops

# All logs
kubectl logs -f -l app=cancer-mlops-api -n cancer-mlops
```

### Update Configuration

```bash
# Edit configmaps.yaml, then:
kubectl apply -f configmaps.yaml
kubectl rollout restart deployment/api-deployment -n cancer-mlops
```

## Cleanup

```bash
# Delete everything
./cleanup.sh

# Or manually
kubectl delete namespace cancer-mlops
```

## Troubleshooting

### Pods Not Starting

```bash
kubectl describe pod <pod-name> -n cancer-mlops
kubectl logs <pod-name> -n cancer-mlops
```

### PVCs Not Binding

```bash
kubectl describe pvc -n cancer-mlops

# Check if storageClass exists
kubectl get storageclass
```

### Service Not Accessible

```bash
# Check endpoints
kubectl get endpoints -n cancer-mlops

# Check pod status
kubectl get pods -n cancer-mlops -o wide
```

## Next Steps

1. **Configure Ingress** - Edit `ingress.yaml` with your domain
2. **Enable TLS** - Use cert-manager for HTTPS
3. **Setup Auto-scaling** - Configure HPA for production
4. **Add Monitoring** - Configure Prometheus alerts
5. **Load Models** - Copy trained models to PVC

For detailed documentation, see [README.md](README.md).

## Support

Having issues? Check:
- `kubectl get events -n cancer-mlops --sort-by='.lastTimestamp'`
- `kubectl get all -n cancer-mlops`
- [Full documentation](README.md)
