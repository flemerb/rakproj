# Rakuten MLOps Project - Phase 2

## Overview

This project implements a complete MLOps pipeline for product classification using microservices architecture.

## Architecture

```
                    +------------------+
                    |   API Gateway    |
                    |    (Port 8080)   |
                    +--------+---------+
                             |
         +-------------------+-------------------+
         |                   |                   |
         v                   v                   v
+----------------+  +----------------+  +----------------+
|  Data Service  |  |Training Service|  |Prediction Svc  |
|  (Port 5001)   |  |  (Port 5002)   |  |  (Port 5003)   |
+----------------+  +----------------+  +----------------+
         |                   |                   |
         +-------------------+-------------------+
                             |
                    +--------v---------+
                    |     MLflow       |
                    |    (Port 5000)   |
                    +------------------+
```

## Services

### 1. MLflow Tracking Server (Port 5000)
- Experiment tracking
- Model registry
- Artifact storage

### 2. Data Service (Port 5001)
- Data loading
- Data preprocessing
- Data status monitoring

### 3. Training Service (Port 5002)
- Model training
- MLflow integration
- Model versioning

### 4. Prediction Service (Port 5003)
- Model inference
- Batch predictions
- Model loading

### 5. API Gateway (Port 8080)
- Request routing
- Service orchestration
- Health monitoring

## Quick Start

### Prerequisites
- Docker
- Docker Compose

### Run All Services

```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### Access Points

| Service | URL |
|---------|-----|
| API Gateway | http://localhost:8080 |
| MLflow UI | http://localhost:5000 |
| Data Service | http://localhost:5001 |
| Training Service | http://localhost:5002 |
| Prediction Service | http://localhost:5003 |

## API Endpoints

### API Gateway

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check all services |
| `/api/v1/predict` | POST | Make prediction |
| `/api/v1/train` | POST | Start training |
| `/api/v1/train/status` | GET | Get training status |
| `/api/v1/data` | GET | Get data status |
| `/api/v1/models` | GET | List registered models |

### Example: Make Prediction

```bash
curl -X POST http://localhost:8080/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Samsung Galaxy S21 smartphone"}'
```

### Example: Start Training

```bash
curl -X POST http://localhost:8080/api/v1/train \
  -H "Content-Type: application/json" \
  -d '{"epochs": 10, "batch_size": 32}'
```

## DVC Pipeline

### Pipeline Stages

```bash
# Run complete pipeline
dvc repro

# Run specific stage
dvc repro --no-commit <stage_name>
```

### Pipeline Definition (dvc.yaml)

```yaml
stages:
  data_import:
    cmd: python src/data/import_raw_data.py
    outs:
      - data/raw
  
  preprocess:
    cmd: python src/data/make_dataset.py data/raw data/preprocessed
    deps:
      - data/raw
    outs:
      - data/preprocessed
  
  train:
    cmd: python src/main.py
    deps:
      - data/preprocessed
    params:
      - train.epochs
      - train.batch_size
    outs:
      - models/best_lstm_model.h5
```

## MLflow Integration

### Tracking Experiments

```python
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("rakuten_classification")

with mlflow.start_run():
    mlflow.log_param("epochs", 10)
    mlflow.log_metric("accuracy", 0.85)
    mlflow.tensorflow.log_model(model, "model")
```

### Viewing Results

Open MLflow UI at http://localhost:5000

## Project Structure

```
rakproj/
├── docker-compose.yml      # Docker orchestration
├── dvc.yaml               # DVC pipeline
├── params.yaml            # Training parameters
├── requirements.txt       # Python dependencies
│
├── services/              # Microservices
│   ├── api_gateway/
│   │   ├── app.py
│   │   └── Dockerfile
│   ├── data_service/
│   │   ├── app.py
│   │   └── Dockerfile
│   ├── training_service/
│   │   ├── app.py
│   │   └── Dockerfile
│   └── prediction_service/
│       ├── app.py
│       └── Dockerfile
│
├── src/                   # Source code
│   ├── main.py
│   ├── data/
│   ├── features/
│   └── models/
│
├── tests/                 # Unit tests
├── data/                  # Data (tracked by DVC)
├── models/                # Trained models
└── mlruns/                # MLflow artifacts
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| MLFLOW_TRACKING_URI | MLflow server URL | http://mlflow:5000 |
| DATA_PATH | Data directory | /app/data |
| MODELS_PATH | Models directory | /app/models |

### Parameters (params.yaml)

```yaml
train:
  epochs: 10
  batch_size: 32
  max_words: 10000
  max_sequence_length: 10
```

## Development

### Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run MLflow locally
mlflow server --backend-store-uri sqlite:///mlruns/mlflow.db --host 0.0.0.0

# Run training
python src/main.py
```

### Running Tests

```bash
pytest tests/
```

## Troubleshooting

### Common Issues

1. **Services not starting**
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

2. **MLflow connection refused**
   - Wait for MLflow to fully start (30-60 seconds)
   - Check MLflow logs: `docker-compose logs mlflow`

3. **Model not found in prediction service**
   - Run training first
   - Check models directory: `ls -la models/`

## Completed Tasks

- [x] MLflow experiment tracking
- [x] DVC data versioning
- [x] DVC pipeline definition
- [x] Microservices architecture
- [x] Docker Compose orchestration
- [x] API Gateway
- [x] Training service with MLflow
- [x] Prediction service
- [x] Data service

## Next Steps

- [ ] Add authentication
- [ ] Implement CI/CD pipeline
- [ ] Add monitoring with Prometheus/Grafana
- [ ] Deploy to Kubernetes
