# Complete Run Guide - Cancer MLOps Platform

This guide will take you from zero to a fully running MLOps platform in ~15 minutes.

---

## 🎯 **Choose Your Path**

1. **[Local Development](#option-1-local-development-python)** - Run on your machine with Python
2. **[Docker](#option-2-docker-deployment)** - Run with containers
3. **[Kubernetes](#option-3-kubernetes-deployment)** - Production deployment

---

# Option 1: Local Development (Python)

## Step 1: Prerequisites Check

Make sure you have:
- ✅ Python 3.8 or higher
- ✅ Git (optional)
- ✅ 2GB free RAM
- ✅ 5GB free disk space

**Check Python version:**
```bash
python --version
# Should show Python 3.8.x or higher
```

---

## Step 2: Setup Environment

### A. Navigate to project directory
```bash
cd C:\AI\Cancer_MLOPs
```

### B. Create virtual environment
```bash
# Windows (CMD)
python -m venv venv
venv\Scripts\activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

---

## Step 3: Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install the project in development mode
pip install -e .
```

**Expected output:** ~50 packages installed successfully

---

## Step 4: Prepare Data

### A. Check if data exists
```bash
# Windows
dir data\raw

# Linux/Mac
ls data/raw
```

### B. If data doesn't exist, download it
The Wisconsin Breast Cancer dataset should be in `data/raw/breast-cancer.csv`

**Note:** The data loading module can fetch it automatically from scikit-learn.

---

## Step 5: Train Models

### Quick Training (Uses Default Config)
```bash
python scripts/train_model.py
```

**This will:**
1. Load the Wisconsin Breast Cancer dataset
2. Preprocess the data
3. Split into train/test sets (75/25)
4. Train 4 models:
   - Logistic Regression
   - Gradient Boosting
   - Neural Network
   - Hybrid Ensemble
5. Evaluate all models
6. Save to `models/` directory
7. Display results

**Expected output:**
```
Training Models...
✓ Logistic Regression - Accuracy: 93%
✓ Gradient Boosting - Accuracy: 96%
✓ Neural Network - Accuracy: 92%
✓ Hybrid Ensemble - Accuracy: 97%

Models saved to: models/hybrid_ensemble/latest/
```

**Time:** ~30-60 seconds

---

## Step 6: Verify Models

```bash
# Check saved models
dir models

# You should see:
# models/
#   ├── hybrid_ensemble/
#   ├── logistic_regression/
#   ├── gradient_boosting/
#   ├── neural_network/
#   └── registry.json
```

---

## Step 7: Start the API

```bash
python src/api/app.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal open!**

---

## Step 8: Test the API

### A. Open a NEW terminal and activate venv again
```bash
cd C:\AI\Cancer_MLOPs
venv\Scripts\activate  # Windows
```

### B. Test health endpoint
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "model_name": "hybrid_ensemble",
  "model_version": "latest",
  "timestamp": "2025-01-30T..."
}
```

### C. Test prediction endpoint

**Windows (PowerShell):**
```powershell
$body = @{
    features = @{
        radius_mean = 17.99
        texture_mean = 10.38
        perimeter_mean = 122.8
        area_mean = 1001.0
        smoothness_mean = 0.1184
        compactness_mean = 0.2776
        concavity_mean = 0.3001
        concave_points_mean = 0.1471
        symmetry_mean = 0.2419
        fractal_dimension_mean = 0.07871
        radius_se = 1.095
        texture_se = 0.9053
        perimeter_se = 8.589
        area_se = 153.4
        smoothness_se = 0.006399
        compactness_se = 0.04904
        concavity_se = 0.05373
        concave_points_se = 0.01587
        symmetry_se = 0.03003
        fractal_dimension_se = 0.006193
        radius_worst = 25.38
        texture_worst = 17.33
        perimeter_worst = 184.6
        area_worst = 2019.0
        smoothness_worst = 0.1622
        compactness_worst = 0.6656
        concavity_worst = 0.7119
        concave_points_worst = 0.2654
        symmetry_worst = 0.4601
        fractal_dimension_worst = 0.1189
    }
    return_probabilities = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Body $body -ContentType "application/json"
```

**Windows (CMD) or Linux/Mac:**
```bash
curl -X POST "http://localhost:8000/predict" ^
  -H "Content-Type: application/json" ^
  -d "{\"features\": {\"radius_mean\": 17.99, \"texture_mean\": 10.38, \"perimeter_mean\": 122.8, \"area_mean\": 1001.0, \"smoothness_mean\": 0.1184, \"compactness_mean\": 0.2776, \"concavity_mean\": 0.3001, \"concave_points_mean\": 0.1471, \"symmetry_mean\": 0.2419, \"fractal_dimension_mean\": 0.07871, \"radius_se\": 1.095, \"texture_se\": 0.9053, \"perimeter_se\": 8.589, \"area_se\": 153.4, \"smoothness_se\": 0.006399, \"compactness_se\": 0.04904, \"concavity_se\": 0.05373, \"concave_points_se\": 0.01587, \"symmetry_se\": 0.03003, \"fractal_dimension_se\": 0.006193, \"radius_worst\": 25.38, \"texture_worst\": 17.33, \"perimeter_worst\": 184.6, \"area_worst\": 2019.0, \"smoothness_worst\": 0.1622, \"compactness_worst\": 0.6656, \"concavity_worst\": 0.7119, \"concave_points_worst\": 0.2654, \"symmetry_worst\": 0.4601, \"fractal_dimension_worst\": 0.1189}, \"return_probabilities\": true}"
```

**Expected response:**
```json
{
  "prediction": 1,
  "diagnosis": "Malignant",
  "confidence": 0.96,
  "probability_benign": 0.04,
  "probability_malignant": 0.96
}
```

---

## Step 9: Access API Documentation

Open your browser and visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

You can test all endpoints interactively here!

---

## Step 10: (Optional) Run MLflow UI

In a NEW terminal:
```bash
cd C:\AI\Cancer_MLOPs
venv\Scripts\activate
mlflow ui --backend-store-uri sqlite:///experiments/mlruns.db
```

Visit: http://localhost:5000

---

## ✅ **Local Development Complete!**

You now have:
- ✅ Trained models (97% accuracy)
- ✅ Running API (http://localhost:8000)
- ✅ API documentation (http://localhost:8000/docs)
- ✅ MLflow tracking (http://localhost:5000)

---

# Option 2: Docker Deployment

## Prerequisites
- ✅ Docker Desktop installed and running
- ✅ 4GB free RAM
- ✅ 10GB free disk space

---

## Step 1: Build Docker Image

```bash
cd C:\AI\Cancer_MLOPs
docker build -f docker/Dockerfile -t cancer-mlops-api:latest .
```

**Time:** ~5-10 minutes (first time)

---

## Step 2: Run with Docker Compose

```bash
docker-compose -f docker/docker-compose.yml up -d
```

**This starts 4 services:**
- API (port 8000)
- MLflow (port 5000)
- Prometheus (port 9090)
- Grafana (port 3000)

---

## Step 3: Verify Services

```bash
# Check running containers
docker ps

# Check logs
docker-compose -f docker/docker-compose.yml logs -f api
```

---

## Step 4: Access Services

- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **MLflow:** http://localhost:5000
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000 (admin/admin)

---

## Step 5: Test API

```bash
curl http://localhost:8000/health
```

---

## Step 6: Stop Services

```bash
docker-compose -f docker/docker-compose.yml down

# To remove volumes (delete data)
docker-compose -f docker/docker-compose.yml down -v
```

---

## ✅ **Docker Deployment Complete!**

You now have:
- ✅ Full MLOps stack in containers
- ✅ Monitoring with Prometheus/Grafana
- ✅ Experiment tracking with MLflow

---

# Option 3: Kubernetes Deployment

## Prerequisites
- ✅ Kubernetes cluster (minikube, kind, or cloud)
- ✅ kubectl installed and configured
- ✅ 8GB RAM, 50GB storage

---

## Step 1: Start Kubernetes Cluster (if using minikube)

```bash
minikube start --cpus=4 --memory=8192
```

---

## Step 2: Build and Tag Docker Image

```bash
cd C:\AI\Cancer_MLOPs

# Build image
docker build -f docker/Dockerfile -t cancer-mlops-api:latest .

# Tag for minikube (if using minikube)
minikube image load cancer-mlops-api:latest
```

---

## Step 3: Update Image Reference

Edit `infrastructure/kubernetes/api-deployment.yaml`:
```yaml
# Line 28: Update this
image: cancer-mlops-api:latest
imagePullPolicy: IfNotPresent  # Change from Always to IfNotPresent for local
```

---

## Step 4: Deploy to Kubernetes

### Option A: One Command
```bash
cd infrastructure/kubernetes
kubectl apply -f all-in-one.yaml
```

### Option B: Using Script (Linux/Mac/WSL)
```bash
cd infrastructure/kubernetes
chmod +x deploy.sh
./deploy.sh
```

### Option C: Manual Steps
```bash
cd infrastructure/kubernetes
kubectl apply -f namespace.yaml
kubectl apply -f configmaps.yaml
kubectl apply -f persistent-volumes.yaml
kubectl apply -f mlflow-deployment.yaml
kubectl apply -f prometheus-deployment.yaml
kubectl apply -f grafana-deployment.yaml
kubectl apply -f api-deployment.yaml
```

---

## Step 5: Wait for Pods

```bash
# Watch pod status
kubectl get pods -n cancer-mlops --watch

# Wait until all pods show "Running"
# Press Ctrl+C when done
```

**Expected output:**
```
NAME                                   READY   STATUS    RESTARTS   AGE
api-deployment-xxxxx                   1/1     Running   0          2m
mlflow-deployment-xxxxx                1/1     Running   0          3m
prometheus-deployment-xxxxx            1/1     Running   0          3m
grafana-deployment-xxxxx               1/1     Running   0          3m
```

---

## Step 6: Access Services

### Option A: Port-Forward (Recommended)

Open 4 terminals and run:

**Terminal 1 - API:**
```bash
kubectl port-forward -n cancer-mlops svc/api-service 8000:8000
```

**Terminal 2 - MLflow:**
```bash
kubectl port-forward -n cancer-mlops svc/mlflow-service 5000:5000
```

**Terminal 3 - Prometheus:**
```bash
kubectl port-forward -n cancer-mlops svc/prometheus-service 9090:9090
```

**Terminal 4 - Grafana:**
```bash
kubectl port-forward -n cancer-mlops svc/grafana-service 3000:3000
```

### Option B: Minikube Service (if using minikube)
```bash
minikube service api-service-external -n cancer-mlops
```

---

## Step 7: Test the Deployment

```bash
# Health check
curl http://localhost:8000/health

# Prediction
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"features": {...}}'
```

---

## Step 8: Check Status

```bash
cd infrastructure/kubernetes
chmod +x status.sh
./status.sh
```

---

## Step 9: Scale the API

```bash
kubectl scale deployment api-deployment -n cancer-mlops --replicas=5

# Verify
kubectl get pods -n cancer-mlops
```

---

## Step 10: Cleanup (when done)

```bash
cd infrastructure/kubernetes
./cleanup.sh

# Or manually
kubectl delete namespace cancer-mlops
```

---

## ✅ **Kubernetes Deployment Complete!**

You now have:
- ✅ Production-grade K8s deployment
- ✅ Auto-scaling capable
- ✅ Full monitoring stack
- ✅ High availability (3 API replicas)

---

# Quick Reference Commands

## Local Development
```bash
# Activate environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Train models
python scripts/train_model.py

# Start API
python src/api/app.py

# Run tests
pytest

# Check code quality
flake8 src/
black src/
```

## Docker
```bash
# Start all services
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop services
docker-compose -f docker/docker-compose.yml down
```

## Kubernetes
```bash
# Deploy
kubectl apply -f infrastructure/kubernetes/all-in-one.yaml

# Status
kubectl get all -n cancer-mlops

# Logs
kubectl logs -f deployment/api-deployment -n cancer-mlops

# Port-forward
kubectl port-forward -n cancer-mlops svc/api-service 8000:8000

# Cleanup
kubectl delete namespace cancer-mlops
```

---

# Troubleshooting

## Issue: "Module not found"
**Solution:**
```bash
pip install -e .
```

## Issue: "Port 8000 already in use"
**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

## Issue: Docker containers won't start
**Solution:**
```bash
docker-compose -f docker/docker-compose.yml down
docker system prune -a
docker-compose -f docker/docker-compose.yml up -d
```

## Issue: Kubernetes pods stuck in "Pending"
**Solution:**
```bash
kubectl describe pod <pod-name> -n cancer-mlops
# Check events for error messages
# Usually: insufficient resources or PVC not binding
```

## Issue: Models not found
**Solution:**
```bash
# Re-train models
python scripts/train_model.py

# Verify models directory
dir models  # Windows
ls models/  # Linux/Mac
```

---

# Next Steps

1. ✅ **Explore API Documentation:** http://localhost:8000/docs
2. ✅ **View MLflow Experiments:** http://localhost:5000
3. ✅ **Check Prometheus Metrics:** http://localhost:9090
4. ✅ **Create Grafana Dashboards:** http://localhost:3000
5. ✅ **Run Tests:** `pytest tests/`
6. ✅ **Train New Models:** Modify configs and retrain
7. ✅ **Deploy to Production:** Use Kubernetes with your cloud provider

---

# Success Checklist

- [ ] Python environment activated
- [ ] Dependencies installed
- [ ] Models trained (97% accuracy achieved)
- [ ] API running on port 8000
- [ ] Health check returns "healthy"
- [ ] Prediction endpoint working
- [ ] API docs accessible
- [ ] (Optional) Docker containers running
- [ ] (Optional) Kubernetes pods running
- [ ] (Optional) MLflow UI accessible
- [ ] (Optional) Monitoring dashboards working

**When all checked, you're ready to go! 🚀**
