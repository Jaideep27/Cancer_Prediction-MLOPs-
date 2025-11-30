# Kubernetes Deployment Guide

This guide provides instructions for deploying the Cancer MLOps platform to a Kubernetes cluster.

## Prerequisites

- Kubernetes cluster (v1.24+)
- kubectl CLI configured
- Docker registry access (for custom images)
- Helm (optional, for easier management)
- NGINX Ingress Controller (for Ingress resources)

## Architecture

The deployment consists of 4 main services:

1. **API Service** - FastAPI application (3 replicas)
2. **MLflow** - Experiment tracking and model registry
3. **Prometheus** - Metrics collection and monitoring
4. **Grafana** - Visualization dashboards

## Quick Start

### 1. Build and Push Docker Image

First, build your API Docker image and push to a registry:

```bash
# Build the image
docker build -f docker/Dockerfile -t <your-registry>/cancer-mlops-api:latest .

# Push to registry
docker push <your-registry>/cancer-mlops-api:latest
```

**Update the image reference in `api-deployment.yaml`:**
```yaml
image: <your-registry>/cancer-mlops-api:latest
```

### 2. Create Namespace

```bash
kubectl apply -f namespace.yaml
```

### 3. Create ConfigMaps

```bash
kubectl apply -f configmaps.yaml
```

### 4. Create Persistent Volumes

```bash
kubectl apply -f persistent-volumes.yaml
```

Wait for PVCs to be bound:
```bash
kubectl get pvc -n cancer-mlops
```

### 5. Deploy Services

Deploy all services in order:

```bash
# Deploy MLflow (dependencies for API)
kubectl apply -f mlflow-deployment.yaml

# Deploy Prometheus
kubectl apply -f prometheus-deployment.yaml

# Deploy Grafana
kubectl apply -f grafana-deployment.yaml

# Deploy API
kubectl apply -f api-deployment.yaml
```

### 6. Setup Ingress (Optional)

If you want to expose services via Ingress:

```bash
# Install NGINX Ingress Controller (if not already installed)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.0/deploy/static/provider/cloud/deploy.yaml

# Apply Ingress configuration
kubectl apply -f ingress.yaml
```

**Update the host in `ingress.yaml`** with your actual domain.

## One-Command Deployment

Deploy everything at once:

```bash
kubectl apply -f namespace.yaml && \
kubectl apply -f configmaps.yaml && \
kubectl apply -f persistent-volumes.yaml && \
sleep 10 && \
kubectl apply -f mlflow-deployment.yaml && \
kubectl apply -f prometheus-deployment.yaml && \
kubectl apply -f grafana-deployment.yaml && \
kubectl apply -f api-deployment.yaml && \
kubectl apply -f ingress.yaml
```

## Verification

### Check Pod Status

```bash
kubectl get pods -n cancer-mlops
```

Expected output:
```
NAME                                    READY   STATUS    RESTARTS   AGE
api-deployment-xxx                      1/1     Running   0          2m
mlflow-deployment-xxx                   1/1     Running   0          3m
prometheus-deployment-xxx               1/1     Running   0          3m
grafana-deployment-xxx                  1/1     Running   0          3m
```

### Check Services

```bash
kubectl get svc -n cancer-mlops
```

### Check Ingress

```bash
kubectl get ingress -n cancer-mlops
```

### View Logs

```bash
# API logs
kubectl logs -f deployment/api-deployment -n cancer-mlops

# MLflow logs
kubectl logs -f deployment/mlflow-deployment -n cancer-mlops

# Prometheus logs
kubectl logs -f deployment/prometheus-deployment -n cancer-mlops

# Grafana logs
kubectl logs -f deployment/grafana-deployment -n cancer-mlops
```

## Accessing Services

### Using Port-Forward (Development)

```bash
# API (port 8000)
kubectl port-forward -n cancer-mlops svc/api-service 8000:8000

# MLflow (port 5000)
kubectl port-forward -n cancer-mlops svc/mlflow-service 5000:5000

# Prometheus (port 9090)
kubectl port-forward -n cancer-mlops svc/prometheus-service 9090:9090

# Grafana (port 3000)
kubectl port-forward -n cancer-mlops svc/grafana-service 3000:3000
```

Then access:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MLflow: http://localhost:5000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### Using NodePort (Cloud/On-Prem)

Services are exposed on NodePort for external access:
- MLflow: `http://<node-ip>:30500`
- Prometheus: `http://<node-ip>:30900`
- Grafana: `http://<node-ip>:30300`

### Using LoadBalancer

The API has a LoadBalancer service (`api-service-external`). Get the external IP:

```bash
kubectl get svc api-service-external -n cancer-mlops
```

Access the API at the EXTERNAL-IP on port 80.

### Using Ingress

If you configured Ingress with domain `cancer-mlops.example.com`:
- API: http://cancer-mlops.example.com/api
- MLflow: http://cancer-mlops.example.com/mlflow
- Prometheus: http://cancer-mlops.example.com/prometheus
- Grafana: http://cancer-mlops.example.com/grafana

Or with subdomain configuration:
- API: http://api.cancer-mlops.example.com
- MLflow: http://mlflow.cancer-mlops.example.com
- Prometheus: http://prometheus.cancer-mlops.example.com
- Grafana: http://grafana.cancer-mlops.example.com

## Testing the Deployment

### Health Check

```bash
# Using port-forward
curl http://localhost:8000/health

# Using LoadBalancer
curl http://<EXTERNAL-IP>/health

# Using Ingress
curl http://api.cancer-mlops.example.com/health
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
    },
    "return_probabilities": true
  }'
```

## Scaling

### Scale API Replicas

```bash
kubectl scale deployment api-deployment -n cancer-mlops --replicas=5
```

### Horizontal Pod Autoscaler

```bash
kubectl autoscale deployment api-deployment -n cancer-mlops \
  --cpu-percent=70 \
  --min=3 \
  --max=10
```

## Configuration Updates

### Update ConfigMap

Edit `configmaps.yaml`, then:

```bash
kubectl apply -f configmaps.yaml
kubectl rollout restart deployment/api-deployment -n cancer-mlops
```

### Update Model

1. Copy new model to the models PVC
2. Update MODEL_VERSION in ConfigMap
3. Restart API pods

## Monitoring

### Prometheus Targets

Check if Prometheus is scraping metrics:

```bash
# Port-forward Prometheus
kubectl port-forward -n cancer-mlops svc/prometheus-service 9090:9090

# Visit http://localhost:9090/targets
```

### Grafana Dashboards

```bash
# Port-forward Grafana
kubectl port-forward -n cancer-mlops svc/grafana-service 3000:3000

# Visit http://localhost:3000
# Login: admin/admin
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod events
kubectl describe pod <pod-name> -n cancer-mlops

# Check logs
kubectl logs <pod-name> -n cancer-mlops
```

### PVC Not Binding

```bash
# Check PVC status
kubectl describe pvc <pvc-name> -n cancer-mlops

# Check storage classes
kubectl get sc
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n cancer-mlops

# Check if pods are ready
kubectl get pods -n cancer-mlops
```

### Image Pull Errors

```bash
# Create image pull secret
kubectl create secret docker-registry regcred \
  --docker-server=<registry> \
  --docker-username=<username> \
  --docker-password=<password> \
  -n cancer-mlops

# Update deployment to use secret
# Add to pod spec:
# imagePullSecrets:
# - name: regcred
```

## Cleanup

### Delete All Resources

```bash
kubectl delete namespace cancer-mlops
```

### Delete Individual Components

```bash
kubectl delete -f ingress.yaml
kubectl delete -f api-deployment.yaml
kubectl delete -f grafana-deployment.yaml
kubectl delete -f prometheus-deployment.yaml
kubectl delete -f mlflow-deployment.yaml
kubectl delete -f persistent-volumes.yaml
kubectl delete -f configmaps.yaml
kubectl delete -f namespace.yaml
```

## Production Considerations

### Security

1. **Change default passwords** in Grafana
2. **Use Secrets** for sensitive data instead of ConfigMaps
3. **Enable RBAC** and limit service account permissions
4. **Network Policies** to restrict pod-to-pod communication
5. **Pod Security Policies** to enforce security standards
6. **Enable TLS** for Ingress (use cert-manager)

### High Availability

1. **Multiple replicas** for API (already configured)
2. **Anti-affinity rules** to spread pods across nodes
3. **Resource limits** and requests properly set
4. **Health checks** configured (liveness/readiness)
5. **PodDisruptionBudgets** to maintain availability during updates

### Storage

1. **Use cloud storage** (AWS EBS, GCP PD, Azure Disk) instead of hostPath
2. **Backup PVCs** regularly
3. **Consider using StatefulSets** for MLflow with PostgreSQL backend
4. **Use object storage** (S3, GCS, Azure Blob) for MLflow artifacts

### Monitoring

1. **Set up alerts** in Prometheus (AlertManager)
2. **Configure Grafana dashboards** for all metrics
3. **Log aggregation** (ELK/EFK stack, CloudWatch, Stackdriver)
4. **Distributed tracing** (Jaeger, Zipkin)

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
- name: Deploy to Kubernetes
  run: |
    kubectl set image deployment/api-deployment \
      api=${{ secrets.REGISTRY }}/cancer-mlops-api:${{ github.sha }} \
      -n cancer-mlops
    kubectl rollout status deployment/api-deployment -n cancer-mlops
```

## Resource Requirements

### Minimum

- 4 vCPUs
- 8 GB RAM
- 50 GB storage

### Recommended (Production)

- 8+ vCPUs
- 16+ GB RAM
- 100+ GB storage
- Multi-node cluster with at least 3 nodes

## Support

For issues or questions:
- Check logs: `kubectl logs -f deployment/<name> -n cancer-mlops`
- Check events: `kubectl get events -n cancer-mlops --sort-by='.lastTimestamp'`
- Check pod status: `kubectl describe pod <pod-name> -n cancer-mlops`
