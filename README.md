# Cancer MLOps - Production ML Platform for Breast Cancer Diagnosis

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue)](https://kubernetes.io/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **End-to-end MLOps platform achieving 97% accuracy in breast cancer diagnosis using hybrid ensemble methods with complete CI/CD, monitoring, and cloud-native deployment.**

---

## 🎯 **Overview**

A production-grade MLOps platform for breast cancer diagnosis prediction (Malignant/Benign) using the Wisconsin Breast Cancer dataset. This project demonstrates enterprise-level ML engineering practices including:

- ✅ **Hybrid Ensemble Model** - 97% accuracy combining Logistic Regression, Gradient Boosting, and Neural Networks
- ✅ **REST API** - FastAPI service with automatic OpenAPI documentation
- ✅ **Experiment Tracking** - MLflow integration for model versioning and metrics
- ✅ **Monitoring Stack** - Prometheus + Grafana for observability
- ✅ **Data Quality** - Statistical drift detection and validation
- ✅ **CI/CD Pipelines** - Automated testing, linting, and deployment via GitHub Actions
- ✅ **Cloud-Native** - Docker Compose and Kubernetes deployment with auto-scaling
- ✅ **Production Ready** - Comprehensive testing, logging, and error handling

---

## 📊 **Model Performance**

| Model | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
|-------|----------|-----------|--------|----------|---------|
| Logistic Regression | 93% | 0.93 | 0.93 | 0.93 | 0.97 |
| Gradient Boosting | 96% | 0.96 | 0.96 | 0.96 | 0.99 |
| Neural Network | 92% | 0.92 | 0.92 | 0.92 | 0.96 |
| **Hybrid Ensemble** | **97%** | **0.97** | **0.97** | **0.97** | **0.99** |

---

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    Cancer MLOps Platform                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐          │
│  │  FastAPI │ ───> │  Models  │ ───> │ Response │          │
│  │   API    │      │ Registry │      │  + JSON  │          │
│  └──────────┘      └──────────┘      └──────────┘          │
│       │                  │                                   │
│       ├─────────────────────────────────┐                   │
│       │                 │                │                   │
│       ▼                 ▼                ▼                   │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │ MLflow   │    │Prometheus│    │ Grafana  │             │
│  │Tracking  │    │ Metrics  │    │Dashboard │             │
│  └──────────┘    └──────────┘    └──────────┘             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**4-Service Architecture:**
- **API Service** - FastAPI application (3 replicas, auto-scalable)
- **MLflow** - Experiment tracking and model registry
- **Prometheus** - Metrics collection and alerting
- **Grafana** - Visualization and dashboards

---

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+
- Docker (optional)
- Kubernetes (optional)

### **1. Local Development (5 minutes)**

```bash
# Clone repository
git clone https://github.com/Jaideep27/Cancer_Prediction-MLOPs-.git
cd Cancer_Prediction-MLOPs-

# Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Train models
python scripts/train_model.py

# Start API
python src/api/app.py
```

**Access:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### **2. Docker Deployment (2 minutes)**

```bash
# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Check status
docker ps
```

**Access:**
- API: http://localhost:8000
- MLflow: http://localhost:5000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### **3. Kubernetes Deployment (5 minutes)**

```bash
# Deploy to cluster
kubectl apply -f infrastructure/kubernetes/all-in-one.yaml

# Check status
kubectl get pods -n cancer-mlops

# Access API
kubectl port-forward -n cancer-mlops svc/api-service 8000:8000
```

**Full guides:**
- [Complete Run Guide](COMPLETE_RUN_GUIDE.md) - Detailed setup instructions
- [Kubernetes Guide](infrastructure/kubernetes/README.md) - K8s deployment
- [Quick Start](infrastructure/kubernetes/QUICKSTART.md) - 5-minute K8s setup

---

## 📁 **Project Structure**

```
Cancer_MLOPs/
├── src/                          # Source code
│   ├── api/                      # FastAPI application
│   │   ├── app.py               # Main API server
│   │   ├── schemas.py           # Pydantic models
│   │   └── middleware.py        # Request/response handling
│   ├── models/                   # ML model implementations
│   │   ├── hybrid_ensemble.py   # Best model (97% accuracy)
│   │   ├── logistic_regression.py
│   │   ├── gradient_boosting.py
│   │   ├── neural_network.py
│   │   ├── train.py            # Training orchestration
│   │   ├── predict.py          # Inference
│   │   ├── evaluate.py         # Metrics calculation
│   │   └── registry.py         # Model versioning
│   ├── data/                    # Data processing
│   │   ├── load_data.py        # Data loading
│   │   ├── preprocess.py       # Transformations
│   │   ├── split.py            # Train/test splitting
│   │   └── validate.py         # Quality checks
│   ├── pipelines/               # Orchestration
│   │   ├── training_pipeline.py
│   │   ├── inference_pipeline.py
│   │   └── evaluation_pipeline.py
│   ├── features/                # Feature engineering
│   ├── monitoring/              # Observability
│   │   ├── performance.py
│   │   └── data_drift.py       # KS-test drift detection
│   └── utils/                   # Utilities
│       ├── config.py
│       ├── logger.py
│       └── helpers.py
│
├── configs/                      # Configuration (YAML)
│   ├── model_config.yaml
│   ├── data_config.yaml
│   ├── training_config.yaml
│   ├── deployment_config.yaml
│   └── logging_config.yaml
│
├── tests/                        # Test suite
│   ├── unit/
│   │   ├── test_data_preprocessing.py
│   │   └── test_models.py
│   ├── integration/
│   │   └── test_api.py
│   └── conftest.py
│
├── scripts/                      # Executable scripts
│   ├── train_model.py
│   ├── evaluate_model.py
│   └── batch_predict.py
│
├── docker/                       # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── infrastructure/               # Infrastructure as Code
│   ├── kubernetes/              # K8s manifests + scripts
│   │   ├── all-in-one.yaml     # Complete deployment
│   │   ├── deploy.sh           # Automated deployment
│   │   ├── status.sh           # Status checking
│   │   └── README.md           # Full K8s guide
│   └── terraform/               # Cloud provisioning (future)
│
├── .github/workflows/            # CI/CD pipelines
│   ├── ci.yml                   # Testing & linting
│   ├── cd.yml                   # Deployment
│   └── model_training.yml       # Scheduled training
│
├── docs/                         # Documentation
│   ├── architecture.md
│   ├── model_card.md
│   ├── quick_start.md
│   └── mlops_tools_guide.md
│
├── Makefile                      # Build automation
├── setup.py                      # Package installation
├── requirements.txt              # Dependencies
├── requirements-dev.txt          # Dev dependencies
├── pytest.ini                    # Test configuration
├── .gitignore
├── LICENSE
└── README.md                     # This file
```

---

## 🎯 **Features**

### **Machine Learning**
- ✅ 4 model implementations (LR, GBC, NN, Ensemble)
- ✅ Automated hyperparameter tuning
- ✅ Cross-validation and stratified splitting
- ✅ Model versioning and registry
- ✅ 30 engineered features from Wisconsin dataset

### **API & Services**
- ✅ RESTful API with FastAPI
- ✅ Automatic OpenAPI/Swagger docs
- ✅ Input validation with Pydantic
- ✅ Single and batch predictions
- ✅ Health checks and metrics endpoint
- ✅ CORS support

### **MLOps & Monitoring**
- ✅ MLflow experiment tracking
- ✅ Prometheus metrics collection
- ✅ Grafana dashboards
- ✅ Statistical data drift detection (KS-test)
- ✅ Performance monitoring
- ✅ Structured JSON logging

### **DevOps & Infrastructure**
- ✅ Docker containerization
- ✅ Docker Compose multi-service setup
- ✅ Kubernetes manifests (production-ready)
- ✅ Auto-scaling configuration
- ✅ Persistent storage (7 volumes)
- ✅ Load balancing and ingress

### **CI/CD**
- ✅ GitHub Actions workflows
- ✅ Automated testing (pytest)
- ✅ Code quality checks (black, flake8, mypy)
- ✅ Security scanning
- ✅ Automated deployments
- ✅ Scheduled model retraining

---

## 📖 **Usage**

### **Training Models**

```python
from src.pipelines.training_pipeline import TrainingPipeline

pipeline = TrainingPipeline()
results = pipeline.run(
    data_filepath="data/raw/breast-cancer.csv",
    save_models=True,
    version="1.0"
)

print(f"Best model: {results['best_model']}")
print(f"Accuracy: {results['metrics']['accuracy']:.2%}")
```

### **Making Predictions**

**Python:**
```python
from src.pipelines.inference_pipeline import InferencePipeline

pipeline = InferencePipeline(
    model_name="hybrid_ensemble",
    model_version="latest"
)

result = pipeline.predict_single({
    "radius_mean": 17.99,
    "texture_mean": 10.38,
    # ... 28 more features
})

print(f"Diagnosis: {result['diagnosis']}")
print(f"Confidence: {result['confidence']:.2%}")
```

**cURL:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "radius_mean": 17.99,
      "texture_mean": 10.38,
      ...
    },
    "return_probabilities": true
  }'
```

**Response:**
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

## 🧪 **Testing**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test suite
pytest tests/unit/
pytest tests/integration/

# Run with verbose output
pytest -v
```

**Coverage:** >80%

---

## 🔧 **Configuration**

All configuration is managed through YAML files in `configs/`:

**model_config.yaml** - Model hyperparameters
```yaml
models:
  gradient_boosting:
    n_estimators: 100
    max_depth: 3
    learning_rate: 0.1
```

**data_config.yaml** - Data processing
```yaml
preprocessing:
  scaling: standard
  missing_value_strategy: drop
```

**deployment_config.yaml** - API settings
```yaml
api:
  host: 0.0.0.0
  port: 8000
  workers: 4
```

---

## 🐳 **Docker**

### **Build Image**
```bash
docker build -f docker/Dockerfile -t cancer-mlops-api:latest .
```

### **Run Single Container**
```bash
docker run -p 8000:8000 \
  -v $(pwd)/models:/app/models:ro \
  cancer-mlops-api:latest
```

### **Run Full Stack**
```bash
docker-compose -f docker/docker-compose.yml up -d
```

### **Stop Services**
```bash
docker-compose -f docker/docker-compose.yml down
```

---

## ☸️ **Kubernetes**

### **Quick Deploy**
```bash
kubectl apply -f infrastructure/kubernetes/all-in-one.yaml
```

### **Using Helper Scripts**
```bash
cd infrastructure/kubernetes
./deploy.sh    # Deploy
./status.sh    # Check status
./update.sh    # Update deployment
./cleanup.sh   # Remove deployment
```

### **Manual Deployment**
```bash
kubectl apply -f infrastructure/kubernetes/namespace.yaml
kubectl apply -f infrastructure/kubernetes/configmaps.yaml
kubectl apply -f infrastructure/kubernetes/persistent-volumes.yaml
kubectl apply -f infrastructure/kubernetes/api-deployment.yaml
kubectl apply -f infrastructure/kubernetes/mlflow-deployment.yaml
kubectl apply -f infrastructure/kubernetes/prometheus-deployment.yaml
kubectl apply -f infrastructure/kubernetes/grafana-deployment.yaml
```

### **Scaling**
```bash
# Manual scaling
kubectl scale deployment api-deployment -n cancer-mlops --replicas=5

# Auto-scaling
kubectl autoscale deployment api-deployment -n cancer-mlops \
  --cpu-percent=70 --min=3 --max=10
```

**Full documentation:** [infrastructure/kubernetes/README.md](infrastructure/kubernetes/README.md)

---

## 📊 **Monitoring**

### **MLflow**
```bash
# Start MLflow UI
mlflow ui --backend-store-uri sqlite:///experiments/mlruns.db

# Visit http://localhost:5000
```

Track experiments, compare models, and manage model registry.

### **Prometheus**
Visit http://localhost:9090 to:
- Query metrics
- View targets
- Check service health

### **Grafana**
Visit http://localhost:3000 (admin/admin) to:
- View dashboards
- Create alerts
- Monitor API performance

---

## 🔄 **CI/CD**

### **GitHub Actions Workflows**

**.github/workflows/ci.yml** - Continuous Integration
- Runs on: Push to main/develop, Pull Requests
- Python versions: 3.8, 3.9, 3.10
- Steps:
  - Lint (flake8, black)
  - Type checking (mypy)
  - Run tests (pytest)
  - Security scan (bandit, safety)
  - Upload coverage

**.github/workflows/cd.yml** - Continuous Deployment
- Runs on: Push to main (after CI passes)
- Steps:
  - Build Docker image
  - Push to registry
  - Deploy to production

**.github/workflows/model_training.yml** - Scheduled Training
- Runs: Weekly (configurable)
- Steps:
  - Train models
  - Evaluate performance
  - Register best model
  - Create artifacts

---

## 🛠️ **Development**

### **Setup Development Environment**
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run pre-commit manually
pre-commit run --all-files
```

### **Code Quality**
```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/

# All checks
make lint
```

### **Makefile Commands**
```bash
make install       # Install dependencies
make test          # Run tests
make lint          # Code quality checks
make format        # Format code
make train         # Train models
make serve         # Start API
make docker-build  # Build Docker image
make docker-run    # Run Docker Compose
make clean         # Clean cache files
```

---

## 📚 **Documentation**

- **[Complete Run Guide](COMPLETE_RUN_GUIDE.md)** - Step-by-step setup for all deployment options
- **[Architecture](docs/architecture.md)** - System design and patterns
- **[Model Card](docs/model_card.md)** - Model documentation
- **[Quick Start](docs/quick_start.md)** - Get started in 5 minutes
- **[MLOps Tools](docs/mlops_tools_guide.md)** - MLflow, Prometheus, Grafana guides
- **[Kubernetes](infrastructure/kubernetes/README.md)** - Complete K8s deployment guide
- **[API Documentation](http://localhost:8000/docs)** - Interactive Swagger UI (when running)

---

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Run linters (`make lint`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

**Contribution Guidelines:**
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Ensure all tests pass
- Maintain >80% code coverage

---

## 🔒 **Security**

- ✅ Input validation with Pydantic
- ✅ No hardcoded credentials
- ✅ Environment-based configuration
- ✅ Security scanning in CI/CD
- ✅ Dependency vulnerability checks
- ⚠️ Change default passwords in production (Grafana)
- ⚠️ Use Secrets for sensitive data in K8s

**Report security issues:** jaideepch007@gmail.com (private)

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **Dataset:** [Wisconsin Breast Cancer Dataset](https://archive.ics.uci.edu/ml/datasets/Breast+Cancer+Wisconsin+(Diagnostic)) - UCI Machine Learning Repository
- **Libraries:** scikit-learn, MLxtend, FastAPI, MLflow, Prometheus, Grafana
- **Community:** Open-source contributors and ML community

---

## 📧 **Contact**

**Jaideep Chandrasekharuni**
- Email: jaideepch007@gmail.com
- GitHub: [@Jaideep27](https://github.com/Jaideep27)

**Project Link:** [https://github.com/Jaideep27/Cancer_Prediction-MLOPs-](https://github.com/Jaideep27/Cancer_Prediction-MLOPs-)

---

## 📊 **Project Statistics**

| Metric | Value |
|--------|-------|
| **Lines of Code** | 5,000+ |
| **Python Files** | 41 |
| **Test Coverage** | >80% |
| **Docker Images** | 1 custom + 3 official |
| **Kubernetes Manifests** | 10 YAML files |
| **CI/CD Workflows** | 3 pipelines |
| **Model Accuracy** | 97% |
| **API Response Time** | <50ms |

---

## 🎓 **Citation**

If you use this project in your research or work, please cite:

```bibtex
@software{cancer_mlops_2025,
  author = {Jaideep Chandrasekharuni},
  title = {Cancer MLOps: Production ML Platform for Breast Cancer Diagnosis},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/Jaideep27/Cancer_Prediction-MLOPs-}
}
```

---

## ⭐ **Star History**

If you find this project useful, please consider giving it a star! ⭐

---

<div align="center">

**Built with ❤️ using Python, FastAPI, scikit-learn, Docker, and Kubernetes**

[Documentation](docs/) • [Issues](https://github.com/Jaideep27/Cancer_Prediction-MLOPs-/issues) • [Pull Requests](https://github.com/Jaideep27/Cancer_Prediction-MLOPs-/pulls)

</div>
