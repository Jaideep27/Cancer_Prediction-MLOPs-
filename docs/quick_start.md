# Quick Start Guide

This guide will help you get the Cancer MLOps project up and running in minutes.

## Prerequisites

- Python 3.8 or higher
- Git (for version control)
- Docker (optional, for containerized deployment)

## Installation Steps

### 1. Setup Environment

```bash
# Navigate to project directory
cd C:\AI\Cancer_MLOPs

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
# source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

### 2. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install the package
pip install -e .

# Optional: Install development dependencies
pip install -r requirements-dev.txt
```

### 3. Verify Installation

```bash
# Check Python packages
pip list | grep cancer-mlops

# Run a simple test
python -c "from src.utils.config import load_config; print('Installation successful!')"
```

## Training Your First Model

### Quick Training

```bash
# Train all models with default settings
python scripts/train_model.py --version 1.0
```

This will:
- Load and validate the breast cancer dataset
- Preprocess the data
- Train 4 models (Logistic Regression, Gradient Boosting, Neural Network, Hybrid Ensemble)
- Evaluate all models
- Save models to the registry
- Generate `training_results.json`

**Expected output:**
```
================================================================================
TRAINING COMPLETE
================================================================================

Best Model: hybrid_ensemble
Accuracy: 0.972
F1 Score: 0.970

Results saved to: training_results.json
================================================================================
```

### Training Time

- Logistic Regression: ~2 seconds
- Gradient Boosting: ~10 seconds
- Neural Network: ~15 seconds
- Hybrid Ensemble: ~5 seconds
- **Total: ~30-40 seconds**

## Running the API

### Start the API Server

```bash
# Development mode (with auto-reload)
python src/api/app.py

# Or using Make
make serve-dev
```

The API will start at `http://localhost:8000`

### Test the API

1. **Open your browser** and visit:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

2. **Make a prediction** using curl:

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
      "concave points_mean": 0.1471,
      "symmetry_mean": 0.2419,
      "fractal_dimension_mean": 0.07871,
      "radius_se": 1.095,
      "texture_se": 0.9053,
      "perimeter_se": 8.589,
      "area_se": 153.4,
      "smoothness_se": 0.006399,
      "compactness_se": 0.04904,
      "concavity_se": 0.05373,
      "concave points_se": 0.01587,
      "symmetry_se": 0.03003,
      "fractal_dimension_se": 0.006193,
      "radius_worst": 25.38,
      "texture_worst": 17.33,
      "perimeter_worst": 184.6,
      "area_worst": 2019.0,
      "smoothness_worst": 0.1622,
      "compactness_worst": 0.6656,
      "concavity_worst": 0.7119,
      "concave points_worst": 0.2654,
      "symmetry_worst": 0.4601,
      "fractal_dimension_worst": 0.1189
    },
    "return_probabilities": true
  }'
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

## Docker Deployment (Optional)

### Using Docker Compose

```bash
# Build and start all services
docker-compose -f docker/docker-compose.yml up -d

# Check status
docker-compose -f docker/docker-compose.yml ps
```

This starts:
- **API**: http://localhost:8000
- **MLflow**: http://localhost:5000
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### Stop Services

```bash
docker-compose -f docker/docker-compose.yml down
```

## Common Commands

### Using Make

```bash
# Show all available commands
make help

# Install dependencies
make install

# Run tests
make test

# Format code
make format

# Start API
make serve

# Start MLflow
make mlflow

# Clean cache files
make clean
```

### Using Python Scripts

```bash
# Train models
python scripts/train_model.py --version 1.0

# Evaluate models
python scripts/evaluate_model.py

# Batch predictions
python scripts/batch_predict.py \
  --input data/test.csv \
  --output predictions.csv

# Run EDA
python scripts/run_eda.py --output-dir eda_output
```

## Exploratory Data Analysis

```bash
# Generate visualizations and statistics
python scripts/run_eda.py

# Output files in eda_output/:
# - feature_distributions.png
# - correlation_matrix.png
# - target_distribution.png
# - summary_statistics.csv
# - missing_values.csv
```

## Model Evaluation

```bash
# Evaluate all models
python scripts/evaluate_model.py

# Evaluate specific model
python scripts/evaluate_model.py --model hybrid_ensemble

# Specify test data
python scripts/evaluate_model.py --test-data data/custom_test.csv
```

## Batch Predictions

```bash
# Make predictions on a CSV file
python scripts/batch_predict.py \
  --input data/processed/test.csv \
  --output predictions.csv \
  --model hybrid_ensemble \
  --version latest
```

Output CSV will include:
- All original columns
- `prediction`: 0 (Benign) or 1 (Malignant)
- `diagnosis`: "Benign" or "Malignant"
- `probability_benign`: Probability of benign diagnosis
- `probability_malignant`: Probability of malignant diagnosis

## Monitoring with MLflow

```bash
# Start MLflow UI
make mlflow
# Or: mlflow ui --backend-store-uri ./experiments/mlruns

# Open browser to http://localhost:5000

# View:
# - Experiment runs
# - Model parameters
# - Training metrics
# - Model artifacts
```

## Troubleshooting

### Issue: Module not found

**Solution:**
```bash
# Ensure package is installed in editable mode
pip install -e .
```

### Issue: Model not found

**Solution:**
```bash
# Train models first
python scripts/train_model.py --version 1.0

# Verify models directory
ls models/
```

### Issue: API health check fails

**Solution:**
```bash
# Check if models exist
ls models/hybrid_ensemble/

# Train models if missing
python scripts/train_model.py
```

### Issue: Port already in use

**Solution:**
```bash
# Check what's using port 8000
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000

# Use different port
uvicorn src.api.app:app --port 8001
```

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs for interactive documentation
2. **Review Model Card**: Check `docs/model_card.md` for model details
3. **Read Architecture**: See `docs/architecture.md` for system design
4. **Run Tests**: Execute `make test` to run the test suite
5. **Customize Config**: Edit files in `configs/` directory
6. **Set up CI/CD**: Review `.github/workflows/` for automation
7. **Deploy to Production**: Follow deployment guides in `docs/`

## Getting Help

- **Documentation**: Check `docs/` directory
- **Issues**: GitHub Issues (if repository is set up)
- **API Docs**: http://localhost:8000/docs (when API is running)

## Summary

You've now:
- ✅ Installed the Cancer MLOps project
- ✅ Trained machine learning models
- ✅ Started the API server
- ✅ Made your first prediction

**Congratulations!** You're ready to use the Cancer MLOps platform.
