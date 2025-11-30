# Cancer MLOps - Breast Cancer Prediction Platform

[![CI](https://github.com/yourusername/cancer-mlops/workflows/CI/badge.svg)](https://github.com/yourusername/cancer-mlops/actions)
[![codecov](https://codecov.io/gh/yourusername/cancer-mlops/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/cancer-mlops)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready MLOps pipeline for breast cancer prediction using ensemble machine learning. This project demonstrates best practices in ML engineering, including automated training pipelines, model serving via REST API, monitoring, and CI/CD.

## Overview

This project implements a complete MLOps workflow for breast cancer diagnosis prediction using the Wisconsin Breast Cancer dataset. It combines three machine learning models (Logistic Regression, Gradient Boosting, Neural Network) into a hybrid ensemble achieving **97% accuracy**.

### Key Features

- **Modular Codebase**: Clean separation of data processing, feature engineering, model training, and inference
- **Multiple Models**: Logistic Regression, Gradient Boosting, Neural Network, and Hybrid Ensemble
- **REST API**: FastAPI-based service for real-time predictions
- **Experiment Tracking**: MLflow integration for tracking experiments and model versions
- **Model Registry**: Centralized model versioning and management
- **Monitoring**: Performance monitoring and data drift detection
- **Containerization**: Docker and Docker Compose for easy deployment
- **Kubernetes**: Production-ready Kubernetes manifests with auto-scaling, ingress, and persistent storage
- **CI/CD**: Automated testing, linting, and deployment pipelines
- **Documentation**: Comprehensive documentation and model cards

## Project Structure

```
Cancer_MLOPs/
├── src/                      # Source code
│   ├── data/                # Data loading and preprocessing
│   ├── features/            # Feature engineering
│   ├── models/              # Model implementations
│   ├── pipelines/           # Training and inference pipelines
│   ├── api/                 # FastAPI application
│   ├── monitoring/          # Monitoring and logging
│   └── utils/               # Utility functions
├── configs/                  # Configuration files
├── data/                     # Data storage
├── models/                   # Trained models
├── tests/                    # Unit and integration tests
├── scripts/                  # Executable scripts
├── docker/                   # Docker configuration
├── .github/workflows/        # CI/CD pipelines
├── docs/                     # Documentation
└── notebooks/                # Jupyter notebooks (dev only)
```

## Quick Start

### Prerequisites

- Python 3.8+
- Docker (optional)
- Make (optional, but recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/cancer-mlops.git
   cd cancer-mlops
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   make install
   # Or manually:
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Setup directories**
   ```bash
   make setup
   ```

### Training Models

Train all models using the training pipeline:

```bash
make train
# Or manually:
python scripts/train_model.py --version 1.0
```

### Running the API

Start the FastAPI server:

```bash
make serve
# Or manually:
python src/api/app.py
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for interactive API documentation.

### Making Predictions

#### Using the API

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d @example_input.json
```

#### Batch Predictions

```bash
python scripts/batch_predict.py \
  --input data/test.csv \
  --output predictions.csv \
  --model hybrid_ensemble
```

## Usage

### Configuration

All configuration is managed through YAML files in the `configs/` directory:

- `model_config.yaml` - Model hyperparameters
- `data_config.yaml` - Data processing settings
- `training_config.yaml` - Training pipeline settings
- `deployment_config.yaml` - API and deployment settings

### Training Pipeline

The training pipeline provides end-to-end model training:

```python
from src.pipelines.training_pipeline import TrainingPipeline

pipeline = TrainingPipeline()
results = pipeline.run(
    data_filepath="data/raw/breast-cancer.csv",
    save_models=True,
    version="1.0"
)
```

### Inference Pipeline

Make predictions using the inference pipeline:

```python
from src.pipelines.inference_pipeline import InferencePipeline

pipeline = InferencePipeline(
    model_name="hybrid_ensemble",
    model_version="latest"
)

result = pipeline.predict_single(features_dict)
print(f"Diagnosis: {result['diagnosis']}")
print(f"Confidence: {result['confidence']:.2%}")
```

### Model Evaluation

Evaluate trained models:

```bash
make evaluate
# Or manually:
python scripts/evaluate_model.py --model hybrid_ensemble
```

## API Documentation

### Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check
- `POST /predict` - Single prediction
- `POST /batch_predict` - Batch predictions
- `GET /docs` - Swagger UI documentation
- `GET /metrics` - Prometheus metrics (when enabled)

### Example Request

```json
{
  "features": {
    "radius_mean": 17.99,
    "texture_mean": 10.38,
    "perimeter_mean": 122.8,
    "area_mean": 1001.0,
    ...
  },
  "return_probabilities": true
}
```

### Example Response

```json
{
  "prediction": 1,
  "diagnosis": "Malignant",
  "confidence": 0.96,
  "probability_benign": 0.04,
  "probability_malignant": 0.96
}
```

## Docker Deployment

### Build and Run with Docker Compose

```bash
make docker-build
make docker-run
```

This starts:
- Cancer Prediction API (port 8000)
- MLflow Tracking Server (port 5000)
- Prometheus (port 9090)
- Grafana (port 3000)

### Build Docker Image

```bash
docker build -f docker/Dockerfile -t cancer-mlops-api:latest .
```

### Run Container

```bash
docker run -p 8000:8000 \
  -v $(pwd)/models:/app/models:ro \
  cancer-mlops-api:latest
```

## Kubernetes Deployment

Deploy the entire Cancer MLOps platform to a Kubernetes cluster with full orchestration, scaling, and monitoring capabilities.

### Quick Deploy

```bash
# One-command deployment
kubectl apply -f infrastructure/kubernetes/all-in-one.yaml

# Or using the helper script
cd infrastructure/kubernetes
chmod +x deploy.sh
./deploy.sh
```

### Manual Deployment

```bash
cd infrastructure/kubernetes

# 1. Create namespace and configs
kubectl apply -f namespace.yaml
kubectl apply -f configmaps.yaml

# 2. Create storage
kubectl apply -f persistent-volumes.yaml

# 3. Deploy services
kubectl apply -f mlflow-deployment.yaml
kubectl apply -f prometheus-deployment.yaml
kubectl apply -f grafana-deployment.yaml
kubectl apply -f api-deployment.yaml

# 4. Setup ingress (optional)
kubectl apply -f ingress.yaml
```

### Access Services

**Port-forwarding (recommended for development):**

```bash
# API
kubectl port-forward -n cancer-mlops svc/api-service 8000:8000

# MLflow
kubectl port-forward -n cancer-mlops svc/mlflow-service 5000:5000

# Prometheus
kubectl port-forward -n cancer-mlops svc/prometheus-service 9090:9090

# Grafana
kubectl port-forward -n cancer-mlops svc/grafana-service 3000:3000
```

**Using Ingress:**
- Configure your domain in `ingress.yaml`
- Access at: `http://your-domain.com/api`

**Using LoadBalancer:**
```bash
kubectl get svc api-service-external -n cancer-mlops
# Access via EXTERNAL-IP
```

### Management Scripts

```bash
# Check deployment status
./status.sh

# Update deployment
./update.sh

# Cleanup
./cleanup.sh
```

### Scaling

```bash
# Scale API replicas
kubectl scale deployment api-deployment -n cancer-mlops --replicas=5

# Auto-scaling
kubectl autoscale deployment api-deployment -n cancer-mlops \
  --cpu-percent=70 --min=3 --max=10
```

For detailed Kubernetes documentation, see [infrastructure/kubernetes/README.md](infrastructure/kubernetes/README.md).

## Development

### Running Tests

```bash
make test           # Run all tests
make test-unit      # Run unit tests only
make test-integration  # Run integration tests only
```

### Code Quality

```bash
make lint       # Run linters
make format     # Format code with black and isort
```

### Pre-commit Hooks

```bash
make pre-commit-install  # Install pre-commit hooks
make pre-commit-run      # Run hooks manually
```

## Monitoring

### MLflow

Start MLflow UI to track experiments:

```bash
make mlflow
```

Visit `http://localhost:5000` to view experiments, metrics, and models.

### Prometheus & Grafana

Monitor API performance with Prometheus and Grafana:

```bash
docker-compose -f docker/docker-compose.yml up prometheus grafana
```

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (admin/admin)

## Model Performance

| Model                   | Accuracy | Precision | Recall | F1 Score | ROC AUC |
|-------------------------|----------|-----------|--------|----------|---------|
| Logistic Regression     | 93%      | 0.93      | 0.93   | 0.93     | 0.97    |
| Gradient Boosting       | 96%      | 0.96      | 0.96   | 0.96     | 0.99    |
| Neural Network          | 92%      | 0.92      | 0.92   | 0.92     | 0.96    |
| **Hybrid Ensemble**     | **97%**  | **0.97**  | **0.97** | **0.97** | **0.99** |

## CI/CD

The project includes GitHub Actions workflows for:

- **Continuous Integration**: Automated testing, linting, and security checks
- **Continuous Deployment**: Docker image building and deployment
- **Model Training**: Scheduled and on-demand model training

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Wisconsin Breast Cancer Dataset - UCI Machine Learning Repository
- Scikit-learn and MLxtend for ML algorithms
- FastAPI for the web framework
- The open-source community

## Contact

Your Name - your.email@example.com

Project Link: [https://github.com/yourusername/cancer-mlops](https://github.com/yourusername/cancer-mlops)

## Citation

If you use this project in your research, please cite:

```bibtex
@software{cancer_mlops,
  author = {Your Name},
  title = {Cancer MLOps: Production ML Pipeline for Breast Cancer Prediction},
  year = {2025},
  url = {https://github.com/yourusername/cancer-mlops}
}
```
