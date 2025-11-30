# Cancer MLOps - System Architecture

## Overview

The Cancer MLOps platform is designed as a production-ready machine learning system following best practices in MLOps. The architecture separates concerns into distinct layers for maintainability, scalability, and testability.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│  (API Clients, Web UI, CLI, Jupyter Notebooks)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                      API Layer (FastAPI)                         │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐           │
│  │  /predict   │  │ /batch_predict│  │   /health   │           │
│  └─────────────┘  └──────────────┘  └─────────────┘           │
│         Middleware (Logging, CORS, Rate Limiting)               │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                   Pipeline Layer                                 │
│  ┌──────────────────┐  ┌────────────────┐  ┌─────────────────┐ │
│  │Training Pipeline │  │Inference Pipe  │  │Evaluation Pipe  │ │
│  └──────────────────┘  └────────────────┘  └─────────────────┘ │
└─────┬──────────────────────┬────────────────────┬───────────────┘
      │                      │                    │
┌─────▼──────┐    ┌─────────▼────────┐    ┌──────▼──────┐
│   Data     │    │     Models        │    │ Monitoring  │
│   Layer    │    │     Layer         │    │   Layer     │
└────────────┘    └──────────────────┘    └─────────────┘
      │                      │                    │
┌─────▼──────────────────────▼────────────────────▼───────────────┐
│                    Storage Layer                                 │
│  ┌──────────┐  ┌────────────┐  ┌──────────┐  ┌──────────────┐ │
│  │   Data   │  │   Models   │  │   Logs   │  │  Experiments │ │
│  └──────────┘  └────────────┘  └──────────┘  └──────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

## Layer Descriptions

### 1. API Layer

**Technology:** FastAPI
**Responsibility:** HTTP interface for model serving

**Components:**
- **Endpoints** (`src/api/endpoints.py`): RESTful API routes
- **Schemas** (`src/api/schemas.py`): Pydantic models for validation
- **Middleware** (`src/api/middleware.py`): Request logging, CORS, error handling
- **App** (`src/api/app.py`): FastAPI application initialization

**Features:**
- Request/response validation
- Automatic OpenAPI documentation
- Error handling and logging
- Health checks
- CORS support

### 2. Pipeline Layer

**Responsibility:** Orchestration of ML workflows

**Training Pipeline** (`src/pipelines/training_pipeline.py`):
- Data loading and validation
- Preprocessing
- Feature engineering
- Model training
- Evaluation
- Model registry

**Inference Pipeline** (`src/pipelines/inference_pipeline.py`):
- Model loading
- Feature preparation
- Prediction generation
- Batch processing

**Evaluation Pipeline** (`src/pipelines/evaluation_pipeline.py`):
- Model comparison
- Performance metrics
- Result reporting

### 3. Data Layer

**Responsibility:** Data management and preprocessing

**Components:**
- **Load** (`src/data/load_data.py`): Data loading utilities
- **Preprocess** (`src/data/preprocess.py`): Data transformation
- **Validate** (`src/data/validate.py`): Data quality checks
- **Split** (`src/data/split.py`): Train/test splitting

**Features:**
- Configurable preprocessing
- Data validation
- Stratified splitting
- Caching

### 4. Models Layer

**Responsibility:** ML model implementations

**Components:**
- **Base Model** (`src/models/base_model.py`): Abstract base class
- **Individual Models**: LR, GBC, NN implementations
- **Ensemble** (`src/models/hybrid_ensemble.py`): Voting classifier
- **Trainer** (`src/models/train.py`): Training orchestration
- **Predictor** (`src/models/predict.py`): Prediction interface
- **Evaluator** (`src/models/evaluate.py`): Metrics calculation
- **Registry** (`src/models/registry.py`): Model versioning

**Features:**
- Consistent interface across models
- Save/load functionality
- Metadata tracking
- Version management

### 5. Monitoring Layer

**Responsibility:** System observability

**Components:**
- **Performance** (`src/monitoring/performance.py`): Model performance tracking
- **Data Drift** (`src/monitoring/data_drift.py`): Distribution shift detection
- **Logging** (`src/monitoring/logging_config.py`): Structured logging

**Integration:**
- Prometheus for metrics
- Grafana for visualization
- MLflow for experiment tracking

### 6. Storage Layer

**Components:**
- **Data Storage**: Raw and processed datasets
- **Model Storage**: Serialized models with metadata
- **Logs**: Application and model logs
- **Experiments**: MLflow tracking data

## Data Flow

### Training Flow

```
Raw Data → Validation → Preprocessing → Feature Engineering
   ↓
Split (Train/Test)
   ↓
Model Training (LR, GBC, NN)
   ↓
Ensemble Creation
   ↓
Evaluation
   ↓
Model Registry
```

### Inference Flow

```
API Request → Schema Validation → Feature Extraction
   ↓
Model Loading (from Registry)
   ↓
Prediction
   ↓
Response Formatting → API Response
```

## Configuration Management

**Configuration Files** (`configs/`):
- `model_config.yaml`: Model hyperparameters
- `data_config.yaml`: Data processing settings
- `training_config.yaml`: Training parameters
- `deployment_config.yaml`: API and deployment settings

**Environment Variables** (`.env`):
- Runtime configuration
- Secrets (API keys, database URLs)
- Feature flags

## Deployment Architecture

### Development

```
Local Machine
├── FastAPI (port 8000)
├── MLflow (port 5000)
└── Jupyter (port 8888)
```

### Production (Docker Compose)

```
Docker Network
├── API Container (FastAPI)
├── MLflow Container
├── Prometheus Container
└── Grafana Container
```

### Cloud Deployment (Example)

```
Load Balancer
├── API Instances (Auto-scaled)
│   └── Container (FastAPI + Model)
├── MLflow Server (ECS/K8s)
├── S3/Blob Storage
│   ├── Models
│   ├── Data
│   └── Artifacts
└── Monitoring Stack
    ├── CloudWatch/Stackdriver
    └── Grafana Cloud
```

## Security Architecture

### API Security

- Input validation (Pydantic)
- Rate limiting
- CORS configuration
- HTTPS in production

### Model Security

- Model versioning and approval
- Access control to registry
- Audit logging

### Data Security

- Data anonymization
- HIPAA compliance considerations
- Encrypted storage (in production)

## Scalability Considerations

### Horizontal Scaling

- API: Multiple uvicorn workers
- Docker: Container replication
- Kubernetes: Pod auto-scaling

### Vertical Scaling

- Model optimization
- Batch prediction
- Caching strategies

### Performance Optimizations

- Model serialization (pickle/joblib)
- Feature preprocessing caching
- Asynchronous API endpoints
- Connection pooling

## Monitoring and Observability

### Metrics

- **Model Metrics**: Accuracy, latency, drift
- **System Metrics**: CPU, memory, requests/sec
- **Business Metrics**: Predictions per day, class distribution

### Logging

- **Application Logs**: Errors, warnings, info
- **Request Logs**: API calls, response times
- **Model Logs**: Predictions, confidence scores

### Alerting

- Performance degradation
- Data drift detection
- System errors
- Resource constraints

## Technology Stack

| Layer | Technology |
|-------|-----------|
| API Framework | FastAPI |
| ML Framework | scikit-learn, MLxtend |
| Data Processing | pandas, numpy |
| Validation | Pydantic |
| Testing | pytest |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Monitoring | Prometheus, Grafana |
| Experiment Tracking | MLflow |
| Documentation | MkDocs |

## Design Patterns

### Patterns Used

1. **Factory Pattern**: Model creation
2. **Singleton Pattern**: Configuration management
3. **Pipeline Pattern**: Data and ML workflows
4. **Repository Pattern**: Model registry
5. **Strategy Pattern**: Different model implementations

### SOLID Principles

- **Single Responsibility**: Each class has one purpose
- **Open/Closed**: Extensible without modification
- **Liskov Substitution**: Base model interface
- **Interface Segregation**: Focused interfaces
- **Dependency Inversion**: Depend on abstractions

## Future Enhancements

### Planned Features

1. **A/B Testing**: Model comparison in production
2. **Feature Store**: Centralized feature management
3. **AutoML**: Hyperparameter optimization
4. **Explainability**: SHAP/LIME integration
5. **Multi-model Serving**: Serve multiple model versions
6. **Streaming Predictions**: Real-time inference
7. **Advanced Monitoring**: Alerting and dashboards

### Scalability Roadmap

1. **Phase 1**: Single-node deployment
2. **Phase 2**: Docker Compose
3. **Phase 3**: Kubernetes orchestration
4. **Phase 4**: Cloud-native services
5. **Phase 5**: Multi-region deployment
