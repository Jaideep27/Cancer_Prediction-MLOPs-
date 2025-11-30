# Complete MLOps Tools Guide

This document explains how to use all the professional MLOps tools included in this project.

## Installed Professional Tools

### 1. **MLflow** - Experiment Tracking & Model Registry

**Purpose**: Track experiments, parameters, metrics, and manage model versions

#### Start MLflow UI
```bash
mlflow ui --backend-store-uri ./experiments/mlruns
# Visit: http://localhost:5000
```

#### Using MLflow in Code
The training pipeline automatically logs to MLflow. To view:

```python
import mlflow

# Start experiment
mlflow.set_experiment("cancer_prediction")

# Log parameters
mlflow.log_param("model_type", "hybrid_ensemble")

# Log metrics
mlflow.log_metric("accuracy", 0.972)

# Log model
mlflow.sklearn.log_model(model, "model")
```

---

### 2. **DVC** - Data Version Control

**Purpose**: Version control for data and model files

#### Initialize DVC
```bash
# Initialize DVC in project
dvc init

# Add data to DVC tracking
dvc add data/raw/breast-cancer.csv

# Commit DVC files to git
git add data/raw/breast-cancer.csv.dvc .gitignore
git commit -m "Add raw data to DVC"
```

#### Setup Remote Storage
```bash
# Local storage
dvc remote add -d local C:/AI/Cancer_MLOPs/dvc-storage

# Or cloud storage
dvc remote add -d myremote s3://mybucket/dvcstore
dvc remote add -d myremote gs://mybucket/dvcstore  # Google Cloud
dvc remote add -d myremote azure://mycontainer  # Azure
```

#### Track Model Files
```bash
# Add models to DVC
dvc add models/hybrid_ensemble/1.0/model.pkl

# Push to remote
dvc push

# Pull from remote
dvc pull
```

---

### 3. **Evidently** - Data Drift & Model Monitoring

**Purpose**: Detect data drift and monitor model performance

#### Generate Data Drift Report
```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
import pandas as pd

# Load reference and current data
reference_data = pd.read_csv("data/processed/train.csv")
current_data = pd.read_csv("data/processed/test.csv")

# Generate report
report = Report(metrics=[
    DataDriftPreset(),
])

report.run(reference_data=reference_data, current_data=current_data)
report.save_html("reports/data_drift_report.html")
```

#### Monitor Model Performance
```python
from evidently.metric_preset import ClassificationPreset

model_report = Report(metrics=[
    ClassificationPreset(),
])

# Include predictions
test_data = current_data.copy()
test_data['prediction'] = model.predict(test_data[features])

model_report.run(reference_data=None, current_data=test_data)
model_report.save_html("reports/model_performance.html")
```

---

###4. **Great Expectations** - Data Validation

**Purpose**: Validate data quality and enforce data contracts

#### Initialize Great Expectations
```bash
great_expectations init
```

#### Create Data Expectations
```python
import great_expectations as ge

# Load data
df = ge.read_csv("data/raw/breast-cancer.csv")

# Create expectations
df.expect_column_values_to_not_be_null("diagnosis")
df.expect_column_values_to_be_in_set("diagnosis", ["M", "B"])
df.expect_column_values_to_be_between("radius_mean", min_value=0, max_value=50)

# Save expectations
df.save_expectation_suite("cancer_data_expectations.json")
```

#### Validate Data
```python
# Run validation
results = df.validate()

if results["success"]:
    print("Data validation passed!")
else:
    print("Data validation failed:")
    print(results)
```

---

### 5. **Prometheus & Grafana** - Metrics & Monitoring

**Purpose**: Monitor API performance and system metrics

#### Start Monitoring Stack
```bash
docker-compose -f docker/docker-compose.yml up prometheus grafana
```

**Access**:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

#### Add Custom Metrics to API
```python
from prometheus_client import Counter, Histogram

# Define metrics
prediction_counter = Counter('predictions_total', 'Total predictions')
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction latency')

# Use in API
@prediction_latency.time()
def make_prediction(features):
    prediction = model.predict(features)
    prediction_counter.inc()
    return prediction
```

---

## Complete MLOps Workflow

### 1. Development Phase

```bash
# 1. Track data with DVC
dvc add data/raw/breast-cancer.csv
git add data/.gitignore data/raw/breast-cancer.csv.dvc
git commit -m "Add raw data"

# 2. Validate data with Great Expectations
python scripts/validate_data.py

# 3. Train models with MLflow tracking
python scripts/train_model.py --version 1.0

# 4. Check experiments in MLflow UI
mlflow ui
```

### 2. Monitoring Phase

```bash
# 1. Check data drift
python scripts/check_drift.py

# 2. Monitor model performance
python scripts/monitor_performance.py

# 3. View metrics in Grafana
# Visit: http://localhost:3000
```

### 3. Deployment Phase

```bash
# 1. Push data to DVC remote
dvc push

# 2. Commit code changes
git add .
git commit -m "Update model"
git push

# 3. Deploy with Docker
docker-compose up -d

# 4. Monitor with Prometheus/Grafana
# Visit: http://localhost:3000
```

---

## Directory Structure for MLOps

```
Cancer_MLOPs/
├── experiments/
│   └── mlruns/              # MLflow experiments
├── .dvc/                    # DVC configuration
│   └── config
├── dvc-storage/             # Local DVC storage
├── reports/                 # Evidently reports
│   ├── data_drift/
│   └── model_performance/
├── great_expectations/      # GE configuration
│   ├── expectations/
│   └── checkpoints/
├── monitoring/
│   ├── prometheus/
│   └── grafana/
└── models/                  # Versioned models
```

---

## Best Practices

### MLflow
- Create separate experiments for different model types
- Log all hyperparameters
- Version your models
- Tag important runs
- Use model registry for production models

### DVC
- Track large files (>10MB) with DVC
- Don't commit data files to git
- Use remote storage for collaboration
- Version data alongside code

### Evidently
- Generate reports weekly
- Set up alerts for drift detection
- Track multiple metrics
- Archive historical reports

### Great Expectations
- Create expectations during EDA
- Validate all incoming data
- Update expectations when data schema changes
- Use in CI/CD pipelines

### Prometheus/Grafana
- Monitor API latency
- Track prediction volumes
- Set up alerts for anomalies
- Create custom dashboards

---

## Integration Examples

### Complete Training Script with MLOps Tools

```python
import mlflow
import great_expectations as ge
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

# 1. Validate data with Great Expectations
df = ge.read_csv("data/raw/breast-cancer.csv")
validation = df.validate()
assert validation["success"], "Data validation failed"

# 2. Start MLflow experiment
mlflow.set_experiment("cancer_prediction")

with mlflow.start_run():
    # Log parameters
    mlflow.log_params({
        "model_type": "hybrid_ensemble",
        "test_size": 0.25,
        "random_state": 0
    })

    # Train model
    model, metrics = train_pipeline.run()

    # Log metrics
    mlflow.log_metrics(metrics)

    # Log model
    mlflow.sklearn.log_model(model, "model")

    # Generate drift report
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=train_data, current_data=test_data)
    mlflow.log_artifact("drift_report.html")

# 3. Track with DVC
os.system("dvc add models/hybrid_ensemble/1.0/model.pkl")
os.system("git add models/hybrid_ensemble/1.0/model.pkl.dvc")
```

---

## Troubleshooting

### MLflow UI not showing experiments
```bash
# Check MLflow tracking URI
echo $MLFLOW_TRACKING_URI

# Restart with correct path
mlflow ui --backend-store-uri ./experiments/mlruns
```

### DVC push fails
```bash
# Check remote configuration
dvc remote list

# Reconfigure remote
dvc remote modify local url C:/AI/Cancer_MLOPs/dvc-storage
```

### Evidently report empty
```python
# Ensure data has same columns
assert set(reference.columns) == set(current.columns)

# Check data types match
print(reference.dtypes)
print(current.dtypes)
```

---

## Automation Scripts

### Check All MLOps Tools
```bash
# Create script: scripts/check_mlops.py
python scripts/check_mlops.py
```

This will verify:
- MLflow server is running
- DVC remotes are configured
- Evidently reports are up to date
- Great Expectations validations pass
- Prometheus metrics are being collected

---

## Production Checklist

Before deploying to production:

- [ ] All data tracked with DVC
- [ ] Model registered in MLflow
- [ ] Data validation with Great Expectations
- [ ] Drift monitoring with Evidently
- [ ] Prometheus metrics configured
- [ ] Grafana dashboards created
- [ ] Alerts configured
- [ ] Documentation updated
- [ ] CI/CD pipelines tested
- [ ] Backup strategy in place

---

## Additional Resources

- **MLflow**: https://mlflow.org/docs/latest/index.html
- **DVC**: https://dvc.org/doc
- **Evidently**: https://docs.evidentlyai.com/
- **Great Expectations**: https://docs.greatexpectations.io/
- **Prometheus**: https://prometheus.io/docs/
- **Grafana**: https://grafana.com/docs/

---

**You now have a complete industry-standard MLOps stack!** 🚀
