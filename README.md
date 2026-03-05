# Rakuten MLOps Project — Phase 2

## Overview

Phase 2 extends the core ML pipeline with a full microservices architecture, JWT-style token authentication, an Apache Airflow orchestration layer, and a browser-based UI. The system classifies product descriptions into 27 categories using an LSTM model trained on Rakuten data.

---

## Architecture

```
                    +------------------+
                    |   Browser UI     |
                    |   (Port 8082)    |
                    +--------+---------+
                             |
                    +--------v---------+
                    |   API Gateway    |
                    |   (Port 8080)    |
                    +---+----+----+----+
                        |    |    |
           +------------+    |    +------------+
           |                 |                 |
           v                 v                 v
  +----------------+ +----------------+ +----------------+
  |  Data Service  | |Training Service| |Prediction Svc  |
  |  (Port 5001)   | |  (Port 5002)   | |  (Port 5003)   |
  +----------------+ +----------------+ +----------------+
           |                 |                 |
           +--------+--------+-----------------+
                    |
           +--------v---------+    +------------------+
           |     MLflow       |    |  Auth Service    |
           |   (Port 5000)    |    |  (Port 5004)     |
           +------------------+    +------------------+
                    |
           +--------v---------+
           |  Apache Airflow  |
           |   (Port 8081)    |
           +------------------+
```

All protected API calls pass through the **Auth Service** for token verification. Admin-level operations (retraining, data management) are additionally gated by role.

---

## Services

### API Gateway (Port 8080)
- Central entry point for all client requests
- Routes to Data, Training, and Prediction services
- Verifies Bearer tokens with the Auth Service on every protected route
- Triggers Airflow DAGs for prediction and retraining workflows
- Proxies `/admin/users` to the Auth Service

### Auth Service (Port 5004)  *(new in Phase 2)*
- SQLite-backed user store
- `POST /auth/login` — returns a session token
- `POST /auth/verify` — validates tokens (called internally by the gateway)
- `GET/POST /admin/users`, `DELETE /admin/users/<id>` — admin-only user management
- Default admin credentials: `admin` / `admin123` (change in production)

### Data Service (Port 5001)
- `/data/load` — loads raw data
- `/data/preprocess` — runs text preprocessing
- `/data/split` — train/test split
- `/data/status` — reports current data state

### Training Service (Port 5002)
- `/train/start` — starts a training run (logs to MLflow)
- `/train/status` — reports whether training is active
- `/train/metrics` — returns latest metrics
- `/models/list` — lists registered models

### Prediction Service (Port 5003)
- `/predict` — single-text classification
- `/predict/batch` — batch classification
- `/model/load` — (re)loads the latest model from disk
- `/model/info` — returns active model metadata

### MLflow Tracking Server (Port 5000)
- Experiment and run tracking
- Model registry
- Artifact storage (SQLite backend + local artifact root)

### Apache Airflow (Port 8081)  *(new in Phase 2)*
Three DAGs are defined:

| DAG | Trigger | Steps |
|-----|---------|-------|
| `rakproj_ml_pipeline` | Daily / manual | import → preprocess → train |
| `predict_pipeline` | API-triggered | ensure model loaded → predict |
| `retrain_pipeline` | Admin-triggered | preprocess → start training → wait → reload model |

### Browser UI (Port 8082)
Static HTML/JS interface for running predictions and (for admins) triggering retraining and managing users.

---

## Quick Start

### Prerequisites
- Docker & Docker Compose

### Run All Services

```bash
# Build and start everything
docker-compose up -d

# Check status
docker-compose ps

# Stream logs
docker-compose logs -f
```

### Access Points

| Service | URL |
|---------|-----|
| UI | http://localhost:8082 |
| API Gateway | http://localhost:8080 |
| Airflow | http://localhost:8081 |
| MLflow UI | http://localhost:5000 |
| Auth Service | http://localhost:5004 |
| Data Service | http://localhost:5001 |
| Training Service | http://localhost:5002 |
| Prediction Service | http://localhost:5003 |

---

## Authentication

All gateway endpoints (except `/health`) require a Bearer token.

### Login

```bash
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
# → {"status": "success", "token": "<TOKEN>", "role": "admin"}
```

Use the returned token in subsequent requests:

```bash
-H "Authorization: Bearer <TOKEN>"
```

---

## API Reference

### Prediction

```bash
# Single prediction
curl -X POST http://localhost:8080/api/v1/predict \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"text": "Samsung Galaxy S21 smartphone 128GB"}'

# Batch prediction
curl -X POST http://localhost:8080/api/v1/predict/batch \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["item one", "item two"]}'
```

### Training  *(admin only)*

```bash
# Trigger retraining via Airflow
curl -X POST http://localhost:8080/api/v1/admin/retrain \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"epochs": 10, "batch_size": 32}'

# Check training status
curl http://localhost:8080/api/v1/train/status \
  -H "Authorization: Bearer <TOKEN>"
```

### Data & Models

```bash
# Data status
curl http://localhost:8080/api/v1/data \
  -H "Authorization: Bearer <TOKEN>"

# List registered models
curl http://localhost:8080/api/v1/models \
  -H "Authorization: Bearer <TOKEN>"
```

### User Management  *(admin only)*

```bash
# List users
curl http://localhost:8080/admin/users \
  -H "Authorization: Bearer <ADMIN_TOKEN>"

# Create user
curl -X POST http://localhost:8080/admin/users \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret", "role": "user"}'

# Delete user
curl -X DELETE http://localhost:8080/admin/users/2 \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

---

## Model

The classifier is a Keras LSTM model with the following default hyperparameters (configurable in `params.yaml`):

| Parameter | Default |
|-----------|---------|
| `epochs` | 10 |
| `batch_size` | 32 |
| `max_words` | 10 000 |
| `max_sequence_length` | 10 |
| `embedding_dim` | 128 |
| `lstm_units` | 128 |
| `num_classes` | 27 |
| `optimizer` | adam |
| `loss` | categorical_crossentropy |

A multimodal variant that concatenates image features with text features is also available in `src/main_with_image_and_concatenate_model.py`.

---

## MLflow Integration

Training runs are automatically logged. To inspect results:

```python
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("rakuten_classification")

with mlflow.start_run():
    mlflow.log_params({"epochs": 10, "batch_size": 32})
    mlflow.log_metric("accuracy", 0.85)
    mlflow.tensorflow.log_model(model, "model")
```

Open the MLflow UI at **http://localhost:5000** to browse experiments, compare runs, and promote models to the registry.

---

## DVC Pipeline

Data and model artifacts are versioned with DVC. The pipeline mirrors the Airflow `rakproj_ml_pipeline` DAG:

```bash
# Run the full pipeline
dvc repro

# Run a specific stage without committing
dvc repro --no-commit train
```

See `DVC_SETUP.md` for remote storage configuration.

---

## Project Structure

```
rakproj/
├── docker-compose.yml          # Orchestration
├── params.yaml                 # Model & training hyperparameters
├── requirements.txt
│
├── services/
│   ├── api_gateway/            # Port 8080
│   ├── auth_service/           # Port 5004 (new)
│   ├── data_service/           # Port 5001
│   ├── training_service/       # Port 5002
│   ├── prediction_service/     # Port 5003
│   └── ui/                     # Port 8082 — static web UI
│
├── dags/
│   ├── rakproj_pipeline.py     # Daily ML pipeline
│   ├── predict_dag.py          # On-demand prediction
│   └── retrain_dag.py          # Admin-triggered retraining
│
├── airflow/
│   └── Dockerfile
│
├── src/
│   ├── main.py                 # Text-only LSTM training entry point
│   ├── main_with_image_and_concatenate_model.py
│   ├── predict.py
│   ├── data/
│   ├── features/
│   ├── models/
│   └── visualization/
│
├── tests/
├── MLFLOW_SETUP.md
└── DVC_SETUP.md
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MLFLOW_TRACKING_URI` | MLflow server | `http://mlflow:5000` |
| `DATA_SERVICE_URL` | Data service | `http://data_service:5001` |
| `TRAINING_SERVICE_URL` | Training service | `http://training_service:5002` |
| `PREDICTION_SERVICE_URL` | Prediction service | `http://prediction_service:5003` |
| `AUTH_SERVICE_URL` | Auth service | `http://auth_service:5004` |
| `AIRFLOW_URL` | Airflow webserver | `http://airflow-webserver:8080` |
| `AIRFLOW_USER` | Airflow API user | `admin` |
| `AIRFLOW_PASS` | Airflow API password | `admin` |
| `DB_PATH` | Auth service SQLite DB | `/app/data/users.db` |

---

## Development

### Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start MLflow locally
mlflow server \
  --backend-store-uri sqlite:///mlruns/mlflow.db \
  --default-artifact-root ./mlflow_artifacts \
  --host 0.0.0.0 --port 5000

# Run training directly
python src/main.py
```

### Tests

```bash
pytest tests/
```

### Rebuild after code changes

```bash
docker-compose down
docker-compose up -d --build
```

---

## Troubleshooting

**Services not starting** — rebuild images:
```bash
docker-compose down && docker-compose up -d --build
```

**401 Unauthorized** — token missing or expired; log in again via `/auth/login`.

**403 Forbidden on `/admin/retrain`** — endpoint requires `role: admin`; use the admin account.

**MLflow connection refused** — MLflow takes 30–60 s to initialize; check with `docker-compose logs mlflow`.

**Model not found in prediction service** — training must complete first, or call `/model/load` manually:
```bash
curl -X POST http://localhost:5003/model/load
```

**Airflow DAG not triggering** — confirm the webserver is healthy at http://localhost:8081 and that `AIRFLOW_USER`/`AIRFLOW_PASS` env vars match your Airflow setup.

---

## Completed

- [x] Microservices architecture (Data, Training, Prediction, API Gateway)
- [x] Auth Service with role-based access control
- [x] Apache Airflow orchestration (3 DAGs)
- [x] Browser-based UI
- [x] MLflow experiment tracking & model registry
- [x] DVC data & model versioning
- [x] Docker Compose orchestration

## Next Steps

- [ ] CI/CD pipeline (GitHub Actions / GitLab CI)
- [ ] Monitoring with Prometheus & Grafana
- [ ] HTTPS / production secrets management
- [ ] Kubernetes deployment