# MLflow Setup Guide - Rakuten MLOps Project

## What is MLflow?

MLflow is an open-source platform for managing the machine learning lifecycle. It helps you:

1. **Experiment Tracking**: Log parameters, metrics, and artifacts
2. **Model Registry**: Store and version models
3. **Model Deployment**: Serve models in production

---

## Installation

### 1. Install MLflow

```bash
cd ~/rakproj
source .venv_rakuten/bin/activate
pip install mlflow
```

### 2. Create MLflow directories

```bash
mkdir -p mlruns mlflow_artifacts
```

---

## Running MLflow Server

### Option 1: Local execution

```bash
mlflow server \
    --backend-store-uri sqlite:///mlruns/mlflow.db \
    --default-artifact-root ./mlflow_artifacts \
    --host 0.0.0.0 \
    --port 5000
```

### Option 2: Using Docker Compose

```bash
docker-compose up -d mlflow
```

---

## Accessing MLflow UI

After starting the server, open your browser at:

```
http://localhost:5000
```

---

## Usage in Code

### 1. Setup MLflow

```python
import mlflow
import mlflow.tensorflow

# Set tracking URI
mlflow.set_tracking_uri("http://localhost:5000")

# Create experiment
mlflow.set_experiment("rakuten_classification")
```

### 2. Log experiments

```python
with mlflow.start_run(run_name="lstm_training"):
    # Log parameters
    mlflow.log_param("epochs", 10)
    mlflow.log_param("batch_size", 32)
    mlflow.log_param("learning_rate", 0.001)
    
    # Log metrics
    mlflow.log_metric("accuracy", 0.85)
    mlflow.log_metric("loss", 0.35)
    
    # Log model
    mlflow.tensorflow.log_model(model, "model")
```

---

## File Structure

```
rakproj/
├── mlruns/                    # Experiment storage
│   ├── mlflow.db             # Database
│   └── 0/                    # First experiment
│       └── artifacts/        # Models and files
├── mlflow_artifacts/          # Artifacts
└── docker-compose.yml         # For running MLflow
```

---

## Completed Tasks

- [x] Install MLflow
- [x] Create storage directories
- [x] Modify train_model.py to add MLflowCallback
- [x] Modify main.py to log experiments
- [x] Create docker-compose.yml

---

## Next Steps

1. Start MLflow server
2. Run training with tracking
3. Review results in MLflow UI

---

## Useful Links

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [MLflow TensorFlow Guide](https://mlflow.org/docs/latest/deep-learning/tensorflow/index.html)
