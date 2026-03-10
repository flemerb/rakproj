# Rakuten MLOps Project

**A production-ready ML classification system that categorizes e-commerce product descriptions into 27 Rakuten product categories using an LSTM neural network. Features a complete MLOps pipeline with microservices architecture, experiment tracking, orchestration, and real-time monitoring.**

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Quick Start](#quick-start)
- [Services](#services)
- [Using the Dashboard](#using-the-dashboard)
- [API Reference](#api-reference)
- [ML Model & Pipeline](#ml-model--pipeline)
- [Monitoring & Metrics](#monitoring--metrics)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

---

## Overview

This project implements a complete MLOps workflow for text classification on Rakuten e-commerce data:

- **Classification Task**: Categorize French product descriptions into 27 product categories
- **Model**: LSTM (Long Short-Term Memory) neural network with 128-dimensional embeddings
- **Dataset**: 16,113+ Rakuten product descriptions with balanced sampling (~600 training, ~50 validation per category)
- **Architecture**: Microservices-based with Docker Compose orchestration
- **MLOps Stack**: MLflow, DVC, Apache Airflow, Prometheus, Grafana

### Technology Stack

- **ML Framework**: TensorFlow/Keras
- **Backend**: Flask (Python 3.11)
- **Orchestration**: Apache Airflow
- **Experiment Tracking**: MLflow
- **Data Versioning**: DVC
- **Monitoring**: Prometheus + Grafana
- **Containerization**: Docker & Docker Compose
- **Frontend**: HTML5 + JavaScript (Nginx)

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
           |  Apache Airflow  |    +------------------+
           |   (Port 8081)    |    |   Prometheus     |
           +------------------+    |   (Port 9090)    |
                                   +------------------+
                                            |
                                   +--------v---------+
                                   |     Grafana      |
                                   |   (Port 3000)    |
                                   +------------------+
```

---

## Features

### MLOps Capabilities

- **Experiment Tracking**: All training runs logged to MLflow with metrics, params, and artifacts
- **Data Versioning**: DVC pipeline for reproducible data processing
- **Workflow Orchestration**: Apache Airflow DAG for automated admin-triggered retraining
- **Model Registry**: MLflow model registry for version management
- **Real-time Monitoring**: Prometheus metrics + Grafana dashboards
- **Production Deployment**: Docker Compose with health checks and auto-restart

### Security & Authentication

- **Token-based Auth**: Bearer token authentication for all API endpoints
- **Role-based Access**: Admin and user roles with permission enforcement
- **Protected Endpoints**: Retraining and user management require admin privileges

### User Interface

- **Web Dashboard**: Modern dark-themed UI for predictions and admin tasks
- **Real-time Predictions**: Interactive text classification with confidence scores
- **Admin Panel**: User management and model retraining controls
- **Monitoring Dashboards**: Pre-built Grafana dashboards for system metrics

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- At least 8GB RAM
- Port availability: 3000, 5000-5004, 8080-8082, 9090

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rakproj
   ```

2. **Start all services**
   ```bash
   # Full presentation setup (recommended)
   make presentation

   # Or manual start
   docker-compose up -d
   sleep 90  # Wait for all services to initialize
   ```

3. **Verify health**
   ```bash
   make health
   ```

4. **Access the dashboard**
   Open http://localhost:8082 in your browser
   - Default credentials: `admin` / `admin123`

### Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| **Web Dashboard** | http://localhost:8082 | admin/admin123 |
| **API Gateway** | http://localhost:8080 | - |
| **MLflow UI** | http://localhost:5000 | - |
| **Airflow** | http://localhost:8081 | admin/admin |
| **Grafana** | http://localhost:3000 | admin/admin |
| **Prometheus** | http://localhost:9090 | - |

---

## Services

### API Gateway (Port 8080)

Central routing hub for all client requests.

**Key Endpoints**:
- `GET /health` - System health check
- `GET /metrics` - Prometheus metrics
- `POST /auth/login` - User authentication
- `POST /api/v1/predict` - Single prediction
- `POST /api/v1/predict/batch` - Batch predictions
- `POST /api/v1/admin/retrain` - Trigger model retraining (admin only)
- `GET /api/v1/train/status` - Training status
- `GET /api/v1/models` - List registered models
- `GET/POST /admin/users` - User management (admin only)

**Features**:
- Token verification for all protected routes
- Airflow DAG triggering
- Service health monitoring
- Request routing with error handling

### Auth Service (Port 5004)

User authentication and authorization.

**Routes**:
- `POST /auth/login` - Generate session token
- `POST /auth/verify` - Validate token (internal)
- `GET /admin/users` - List all users (admin only)
- `POST /admin/users` - Create new user (admin only)
- `DELETE /admin/users/<id>` - Delete user (admin only)

**Features**:
- SQLite-backed user store
- SHA256 password hashing
- Role-based access control (admin/user)
- Session token management

**Default Credentials**:
- Username: `admin`
- Password: `admin123`
- Role: admin

**Important**: Change default credentials in production!

### Data Service (Port 5001)

Data loading and preprocessing.

**Routes**:
- `POST /data/load` - Load raw CSV data
- `POST /data/split` - Train/validation/test split
- `POST /data/preprocess` - Text preprocessing pipeline
- `GET /data/status` - Data availability status

**Preprocessing Steps**:
1. HTML/XML tag removal (BeautifulSoup)
2. Text lowercasing
3. Tokenization (NLTK)
4. French stopword removal
5. Lemmatization (WordNet)
6. Sequence generation and padding

### Training Service (Port 5002)

Model training with MLflow integration.

**Routes**:
- `POST /train/start` - Start training (background thread)
- `GET /train/status` - Training progress
- `GET /train/metrics` - Latest training metrics
- `GET /models/list` - List MLflow registered models

**Features**:
- Non-blocking training execution
- MLflow experiment logging (params, metrics, artifacts)
- Prometheus metrics export
- Early stopping and model checkpointing

**Training Process**:
1. Load preprocessed data
2. Build LSTM model with configured hyperparameters
3. Train with callbacks (MLflow, TensorBoard, Early Stopping)
4. Save best model + tokenizer + category mappings
5. Log results to MLflow

### Prediction Service (Port 5003)

Real-time inference API.

**Routes**:
- `POST /predict` - Single text classification
- `POST /predict/batch` - Batch classification
- `POST /model/load` - Reload model from disk
- `GET /model/info` - Active model metadata

**Single Prediction Response Format**:
```json
{
  "status": "success",
  "predicted_class": 12,
  "real_category": "Electronics - Smartphones",
  "original_code": "prdtypecode_40",
  "confidence": 0.923,
  "all_probabilities": [0.001, 0.002, ..., 0.923, ...]
}
```

**Batch Prediction Response Format**:
```json
{
  "status": "success",
  "predictions": [
    {
      "text": "Pull en laine rouge...",
      "predicted_class": 5,
      "category_name": "Clothing",
      "confidence": 0.87
    },
    {
      "text": "Ordinateur portable gaming...",
      "predicted_class": 12,
      "category_name": "Electronics",
      "confidence": 0.91
    }
  ]
}
```

**Note**: Single prediction uses `"real_category"` while batch prediction uses `"category_name"` (implementation inconsistency).

**Features**:
- Automatic text preprocessing
- Confidence score calculation
- Batch processing support
- Latency and confidence metrics

### MLflow Tracking Server (Port 5000)

Experiment tracking and model registry.

**Features**:
- SQLite backend for metadata
- Local artifact storage
- Experiment organization
- Model versioning and promotion
- Metrics comparison and visualization

**Logged Information**:
- Hyperparameters (epochs, batch_size, lstm_units, etc.)
- Training/validation metrics (loss, accuracy)
- Model artifacts (Keras model, tokenizer, mappings)
- Training duration and timestamps

### Apache Airflow (Port 8081)

Workflow orchestration for model retraining.

**Implemented DAG**:

| DAG | Trigger | Description | Steps |
|-----|---------|-------------|-------|
| `retrain_pipeline` | Admin-triggered via API | Model retraining workflow | preprocess → train → wait → reload |

**Retraining Workflow Details**:
1. **preprocess_new_data** - Calls data_service to preprocess latest data
2. **start_training** - Calls training_service to start LSTM training
3. **wait_for_training_completion** - Polls training_service every 10s (max 1 hour)
4. **reload_model_in_prediction_service** - Refreshes model in prediction service

**Configuration Parameters**:
- `epochs` (default: 10)
- `batch_size` (default: 32)

**Access**: http://localhost:8081 (admin/admin)

**Note**: Predictions are handled by the prediction_service microservice, NOT by Airflow. The DAG is only for retraining orchestration.

### Web Dashboard (Port 8082)

Browser-based user interface.

**Features**:
- Login page with role-based access
- Prediction interface with real-time results
- Admin panel for:
  - User management (create/delete users)
  - Model retraining triggers
  - System metrics viewing
- Modern dark theme with responsive design

**Technologies**: HTML5, CSS3, JavaScript (Vanilla), Nginx

### Prometheus (Port 9090)

Metrics collection and time-series database.

**Scraped Services** (every 15s):
- API Gateway: Request counts, latencies, service health
- Data Service: Data loading metrics
- Training Service: Training progress, loss, accuracy
- Prediction Service: Inference latency, confidence, prediction counts

**Metric Examples**:
- `gateway_requests_total{method="POST", endpoint="/api/v1/predict", status="200"}`
- `training_accuracy{split="validation"}`
- `prediction_confidence_bucket{le="0.9"}`
- `prediction_inference_duration_seconds_sum`

### Grafana (Port 3000)

Metrics visualization and monitoring dashboards.

**Pre-configured Dashboard** (`mlops_dashboard.json`):
- Service health status indicators
- Request latency graphs (p50, p95, p99)
- Model prediction confidence distribution
- Training progress curves (loss/accuracy)
- Batch prediction size distribution
- Service availability timeline

**Access**: http://localhost:3000 (admin/admin)

**Data Source**: Prometheus (auto-provisioned)

---

## Using the Dashboard

### 1. Login

1. Navigate to http://localhost:8082
2. Enter credentials:
   - Username: `admin`
   - Password: `admin123`
3. Click "Login"

### 2. Making Predictions

1. After login, you'll see the prediction interface
2. Enter a product description in the text area
   - Example: "Samsung Galaxy S21 smartphone 128GB noir"
   - Example: "Pull en laine rouge pour l'hiver"
3. Click "Predict"
4. View results:
   - Predicted category name
   - Confidence score (percentage)
   - Product type code
   - Full probability distribution

### 3. Admin Panel (Admin Users Only)

**User Management**:
1. Click "Admin Panel" button
2. View list of existing users
3. Create new user:
   - Enter username, password
   - Select role (admin/user)
   - Click "Create User"
4. Delete users by clicking delete icon

**Model Retraining**:
1. In Admin Panel, find "Retrain Model" section
2. Configure parameters:
   - Epochs (default: 10)
   - Batch size (default: 32)
3. Click "Start Retraining"
4. Monitor progress in Airflow UI (http://localhost:8081)
   - Watch the `retrain_pipeline` DAG execution
   - Each task shows status: queued → running → success

### 4. Viewing Metrics

**Grafana Dashboards**:
1. Navigate to http://localhost:3000
2. Login: admin/admin
3. Go to Dashboards → MLOps Dashboard
4. View real-time metrics:
   - Service health
   - Request rates and latencies
   - Model performance
   - Prediction confidence trends

**Prometheus Queries**:
1. Navigate to http://localhost:9090
2. Example queries:
   - `rate(predictions_total[5m])` - Predictions per second
   - `histogram_quantile(0.95, prediction_confidence_bucket)` - 95th percentile confidence
   - `training_accuracy{split="validation"}` - Current validation accuracy

---

## API Reference

### Authentication

All endpoints (except `/health`) require a Bearer token.

**Login**:
```bash
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Response:
# {
#   "status": "success",
#   "token": "a1b2c3d4e5f6...",
#   "role": "admin",
#   "username": "admin"
# }
```

**Use Token in Requests**:
```bash
-H "Authorization: Bearer <TOKEN>"
```

### Prediction Endpoints

**Single Prediction**:
```bash
curl -X POST http://localhost:8080/api/v1/predict \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Samsung Galaxy S21 smartphone 128GB"
  }'

# Response:
# {
#   "status": "success",
#   "predicted_class": 12,
#   "real_category": "Electronics - Smartphones",
#   "original_code": "prdtypecode_40",
#   "confidence": 0.923,
#   "all_probabilities": [0.001, 0.002, ..., 0.923, ...]
# }
```

**Batch Prediction**:
```bash
curl -X POST http://localhost:8080/api/v1/predict/batch \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Pull en laine rouge",
      "Ordinateur portable gaming"
    ]
  }'

# Response:
# {
#   "status": "success",
#   "predictions": [
#     {
#       "text": "Pull en laine rouge",
#       "predicted_class": 5,
#       "category_name": "Clothing",
#       "confidence": 0.87
#     },
#     {
#       "text": "Ordinateur portable gaming",
#       "predicted_class": 12,
#       "category_name": "Electronics",
#       "confidence": 0.91
#     }
#   ]
# }
```

### Training Endpoints (Admin Only)

**Trigger Retraining**:
```bash
curl -X POST http://localhost:8080/api/v1/admin/retrain \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "epochs": 10,
    "batch_size": 32
  }'

# Response:
# {
#   "status": "success",
#   "dag_run_id": "manual__2026-03-10T12:00:00+00:00",
#   "message": "Retraining DAG triggered successfully"
# }
```

**Check Training Status**:
```bash
curl http://localhost:8080/api/v1/train/status \
  -H "Authorization: Bearer <TOKEN>"

# Response:
# {
#   "training_active": true,
#   "current_epoch": 5,
#   "total_epochs": 10,
#   "latest_metrics": {
#     "train_loss": 0.234,
#     "train_accuracy": 0.912,
#     "val_loss": 0.312,
#     "val_accuracy": 0.887
#   }
# }
```

### Data Endpoints

**Data Status**:
```bash
curl http://localhost:8080/api/v1/data \
  -H "Authorization: Bearer <TOKEN>"

# Response:
# {
#   "raw_data_available": true,
#   "preprocessed_data_available": true,
#   "train_samples": 16113,
#   "validation_samples": 1350,
#   "test_samples": 2000
# }
```

### Model Endpoints

**List Registered Models**:
```bash
curl http://localhost:8080/api/v1/models \
  -H "Authorization: Bearer <TOKEN>"

# Response:
# {
#   "models": [
#     {
#       "name": "lstm_rakuten_classifier",
#       "version": 3,
#       "stage": "Production",
#       "last_updated": "2026-03-10T12:00:00Z"
#     }
#   ]
# }
```

### User Management (Admin Only)

**List Users**:
```bash
curl http://localhost:8080/admin/users \
  -H "Authorization: Bearer <ADMIN_TOKEN>"

# Response:
# {
#   "users": [
#     {"id": 1, "username": "admin", "role": "admin"},
#     {"id": 2, "username": "alice", "role": "user"}
#   ]
# }
```

**Create User**:
```bash
curl -X POST http://localhost:8080/admin/users \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "bob",
    "password": "securepass123",
    "role": "user"
  }'

# Response:
# {
#   "status": "success",
#   "user_id": 3,
#   "username": "bob"
# }
```

**Delete User**:
```bash
curl -X DELETE http://localhost:8080/admin/users/3 \
  -H "Authorization: Bearer <ADMIN_TOKEN>"

# Response:
# {"status": "success", "message": "User deleted"}
```

---

## ML Model & Pipeline

### Model Architecture

**TextLSTMModel** (Keras Sequential):

```
Input Layer (sequence of integers)
    ↓
Embedding Layer (128 dimensions, vocabulary size: 10,000)
    ↓
LSTM Layer (128 units, return_sequences=False)
    ↓
Dense Output Layer (27 units, softmax activation)
```

### Hyperparameters

Configured in `params.yaml`:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `epochs` | 10 | Training epochs |
| `batch_size` | 32 | Batch size |
| `max_words` | 10,000 | Maximum vocabulary size |
| `max_sequence_length` | 10 | Padded sequence length |
| `embedding_dim` | 128 | Word embedding dimensions |
| `lstm_units` | 128 | LSTM hidden units |
| `num_classes` | 27 | Output classes (categories) |
| `optimizer` | adam | Optimization algorithm |
| `loss` | categorical_crossentropy | Loss function |

### Data Pipeline

**Data Flow**:

```
AWS S3 (Rakuten Dataset)
    ↓ [import_raw_data.py]
data/raw/
├── X_train_update.csv      (16,113+ descriptions + metadata)
├── X_test_update.csv
└── Y_train_CVw08PX.csv     (product type codes)
    ↓ [make_dataset.py + TextPreprocessor]
data/preprocessed/
├── X_train_update.csv      (cleaned descriptions)
└── Y_train_CVw08PX.csv
    ↓ [train_model.py]
models/
├── best_lstm_model.h5      (trained Keras model)
├── tokenizer_config.json   (Keras tokenizer)
├── mapper.json             (category index mapping)
├── category_names.json     (human-readable names)
└── metrics.json            (training metrics)
```

**Preprocessing Steps**:

1. **HTML/XML Cleaning**: Remove tags with BeautifulSoup
2. **Lowercasing**: Normalize text case
3. **Tokenization**: Split into words (NLTK)
4. **Stopword Removal**: Filter French stopwords
5. **Lemmatization**: Reduce to base forms (WordNet)
6. **Sequence Generation**: Convert to integer sequences (Keras Tokenizer)
7. **Padding**: Pad sequences to max_sequence_length (10 tokens)

### Product Categories

The model classifies into **27 Rakuten product categories**:

Examples include:
- Clothing & Accessories
- Electronics & Computers
- Home & Garden
- Sports & Leisure
- Beauty & Health
- Books & Media
- Toys & Games
- And 20 more categories...

Category mappings stored in:
- `models/mapper.json`: `{class_index → product_type_code}`
- `models/category_names.json`: `{class_index → category_name}`

### Training Callbacks

1. **Early Stopping**: Stops training if validation loss doesn't improve for 3 epochs
2. **Model Checkpoint**: Saves best model based on validation accuracy
3. **TensorBoard**: Logs metrics for visualization
4. **MLflow Callback**: Custom callback logging metrics to MLflow every epoch

### DVC Pipeline

**Stages** (defined in `dvc.yaml`):

1. **data_import**: Download raw data from AWS S3
2. **preprocess**: Clean and prepare data for training
3. **train**: Train LSTM model with MLflow logging

**Run Pipeline**:
```bash
# Full pipeline
dvc repro

# Specific stage
dvc repro train

# Visualize pipeline
dvc dag
```

**DVC Commands**:
```bash
dvc status          # Check if outputs need updating
dvc push           # Push data/models to remote storage
dvc pull           # Pull data/models from remote storage
```

See `DVC_SETUP.md` for remote configuration.

---

## Monitoring & Metrics

### Prometheus Metrics

**API Gateway Metrics**:
- `gateway_requests_total{method, endpoint, status}` - Total requests
- `gateway_request_duration_seconds{method, endpoint}` - Request latency histogram
- `gateway_service_up{service}` - Service health (1=up, 0=down)

**Data Service Metrics**:
- `data_service_requests_total{endpoint, status}` - Request counts
- `data_service_records_loaded{split}` - Records by train/val/test split

**Training Service Metrics**:
- `training_active` - Training status (1=active, 0=idle)
- `training_current_epoch` - Current training epoch
- `training_loss{split}` - Loss by train/validation split
- `training_accuracy{split}` - Accuracy by split
- `training_runs_total` - Total training runs started

**Prediction Service Metrics**:
- `predictions_total{predicted_class}` - Predictions by category
- `prediction_confidence` - Confidence score histogram
- `prediction_inference_duration_seconds` - Inference latency
- `model_loaded` - Model status (1=loaded, 0=not loaded)
- `prediction_batch_size` - Batch size histogram

### Grafana Dashboards

**Pre-built Dashboard** (`monitoring/grafana/dashboards/mlops_dashboard.json`):

**Panels**:
1. **Service Health**: Real-time status of all microservices
2. **Request Rate**: Requests per second by endpoint
3. **Latency Percentiles**: p50, p95, p99 response times
4. **Prediction Confidence**: Distribution of model confidence scores
5. **Training Progress**: Loss and accuracy curves over epochs
6. **Model Performance**: Validation metrics over time
7. **Batch Size Distribution**: Batch prediction sizes
8. **Service Availability**: Uptime timeline for each service

**Accessing Grafana**:
1. Navigate to http://localhost:3000
2. Login: `admin` / `admin`
3. Dashboards → MLOps Dashboard

**Custom Queries**:
Create custom panels with PromQL:
```promql
# Average prediction confidence over 5m
avg(rate(prediction_confidence_sum[5m]) / rate(prediction_confidence_count[5m]))

# Request success rate
sum(rate(gateway_requests_total{status="200"}[5m])) / sum(rate(gateway_requests_total[5m]))

# Training progress
training_accuracy{split="validation"}
```

### Accessing Prometheus

Navigate to http://localhost:9090

**Useful Queries**:

```promql
# Predictions per minute
rate(predictions_total[1m]) * 60

# 95th percentile inference latency
histogram_quantile(0.95, rate(prediction_inference_duration_seconds_bucket[5m]))

# Training accuracy
training_accuracy{split="validation"}

# Gateway error rate
sum(rate(gateway_requests_total{status=~"5.."}[5m])) / sum(rate(gateway_requests_total[5m]))
```

---

## Project Structure

```
rakproj/
├── docker-compose.yml              # Service orchestration (13 containers)
├── params.yaml                     # ML hyperparameters
├── dvc.yaml                        # DVC pipeline definition
├── requirements.txt                # Python dependencies
├── Makefile                        # Automation commands
├── README.md                       # Project README
├── PROJECT_COMPLETE_DOCUMENTATION.md  # This file (100% verified)
│
├── services/                       # Microservices
│   ├── api_gateway/               # Port 8080 - Central router
│   │   ├── app.py                 # Flask application
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── auth_service/              # Port 5004 - Authentication
│   │   ├── app.py                 # User management & token verification
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── data_service/              # Port 5001 - Data management
│   │   ├── app.py                 # Data loading & preprocessing
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── training_service/          # Port 5002 - Model training
│   │   ├── app.py                 # Training orchestration & MLflow
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── prediction_service/        # Port 5003 - Inference
│   │   ├── app.py                 # Single & batch predictions
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── ui/                        # Port 8082 - Web dashboard
│       ├── index.html             # Login & prediction interface
│       ├── Dockerfile
│       └── nginx.conf
│
├── dags/                          # Apache Airflow DAGs
│   └── retrain_dag.py            # Admin-triggered retraining (retrain_pipeline)
│
├── airflow/                       # Airflow configuration
│   └── Dockerfile
│
├── src/                           # Core ML code
│   ├── main.py                   # Training entry point
│   ├── data/
│   │   ├── import_raw_data.py    # AWS S3 data download
│   │   ├── make_dataset.py       # Preprocessing pipeline
│   │   └── check_structure.py    # Data validation
│   ├── features/
│   │   └── build_features.py     # DataImporter, TextPreprocessor
│   ├── models/
│   │   └── train_model.py        # TextLSTMModel, MLflowCallback
│   └── visualization/
│
├── data/
│   ├── raw/                      # Raw CSV files from Rakuten
│   │   ├── X_train_update.csv
│   │   ├── X_test_update.csv
│   │   └── Y_train_CVw08PX.csv
│   └── preprocessed/             # Cleaned data
│       ├── X_train_update.csv
│       └── Y_train_CVw08PX.csv
│
├── models/                        # Trained artifacts
│   ├── best_lstm_model.h5        # Keras model weights
│   ├── tokenizer_config.json     # Tokenizer configuration
│   ├── mapper.json               # {index → product_type_code}
│   ├── category_names.json       # {index → category_name}
│   └── metrics.json              # Training metrics
│
├── monitoring/                    # Monitoring stack
│   ├── prometheus/
│   │   └── prometheus.yml        # Scrape configuration (4 services)
│   └── grafana/
│       ├── provisioning/
│       │   ├── datasources/      # Prometheus datasource
│       │   └── dashboards/       # Dashboard provisioning
│       ├── dashboards/
│       │   └── mlops_dashboard.json  # Pre-built MLOps dashboard
│       └── grafana.ini
│
├── mlruns/                        # MLflow experiments & artifacts
│   ├── mlflow.db                 # SQLite backend
│   └── <experiment_id>/          # Experiment runs
│
├── logs/                          # Application & Airflow logs
├── tests/                         # Unit & integration tests
│   ├── test_data.py
│   ├── test_features.py
│   ├── test_models.py
│   ├── test_model_quality.py
│   └── test_integration.py
│
├── MLFLOW_SETUP.md               # MLflow configuration guide
├── DVC_SETUP.md                  # DVC setup instructions
└── TESTING_GUIDE.md              # Testing procedures
```

---

## Configuration

### Environment Variables

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `MLFLOW_TRACKING_URI` | Training/Prediction | `http://mlflow:5000` | MLflow server address |
| `DATA_SERVICE_URL` | API Gateway | `http://data_service:5001` | Data service URL |
| `TRAINING_SERVICE_URL` | API Gateway | `http://training_service:5002` | Training service URL |
| `PREDICTION_SERVICE_URL` | API Gateway | `http://prediction_service:5003` | Prediction service URL |
| `AUTH_SERVICE_URL` | API Gateway | `http://auth_service:5004` | Auth service URL |
| `AIRFLOW_URL` | API Gateway | `http://airflow-webserver:8080` | Airflow web server |
| `AIRFLOW_USER` | API Gateway | `admin` | Airflow username |
| `AIRFLOW_PASS` | API Gateway | `admin` | Airflow password |
| `DB_PATH` | Auth Service | `/app/data/users.db` | SQLite database path |
| `PREPROCESSED_PATH` | Training/Data | `/app/data/preprocessed` | Processed data location |
| `MODELS_PATH` | Training/Prediction | `/app/models` | Model storage path |

### Makefile Commands

**Quick Operations**:
```bash
make help           # Show all available commands
make presentation   # Full setup: stop → start → wait → verify
make health         # Check all service health endpoints
make quick-check    # Pre-presentation verification
```

**Service Management**:
```bash
make up             # Start all services
make down           # Stop all services
make restart        # Restart all services
make rebuild        # Rebuild and restart
make logs           # Follow service logs
```

**Testing**:
```bash
make test-predict   # Test prediction with sample data
make verify-all     # Comprehensive system verification
```

**Data & Training**:
```bash
make train          # Trigger training locally
make predict        # Test prediction endpoint
```

---

## Development

### Local Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet')"
```

### Running Services Locally

**MLflow Server**:
```bash
mlflow server \
  --backend-store-uri sqlite:///mlruns/mlflow.db \
  --default-artifact-root ./mlflow_artifacts \
  --host 0.0.0.0 --port 5000
```

**Training**:
```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
python src/main.py
```

**Individual Services**:
```bash
# Data service
cd services/data_service
python app.py

# Training service
cd services/training_service
python app.py

# Prediction service
cd services/prediction_service
python app.py
```

### Testing

**Run All Tests**:
```bash
pytest tests/ -v
```

**Test Categories**:
```bash
pytest tests/test_data.py           # Data loading
pytest tests/test_features.py       # Preprocessing
pytest tests/test_models.py         # Model architecture
pytest tests/test_model_quality.py  # Performance tests
pytest tests/test_integration.py    # End-to-end tests
```

**Coverage Report**:
```bash
pytest --cov=src --cov-report=html tests/
```

### Code Changes

**Rebuild After Changes**:
```bash
# Specific service
docker-compose up -d --build <service_name>

# All services
docker-compose down
docker-compose up -d --build
```

**Hot Reload** (for development):
```bash
# Mount code as volume in docker-compose.yml
volumes:
  - ./services/prediction_service:/app
  - ./src:/app/src
```

---

## Troubleshooting

### Common Issues

**Services not starting**
```bash
# Check logs
docker-compose logs <service_name>

# Rebuild images
docker-compose down
docker-compose up -d --build

# Clean restart
docker-compose down -v  # WARNING: Deletes volumes
docker-compose up -d --build
```

**401 Unauthorized**
- Token missing or expired
- Solution: Login again via `POST /auth/login`

**403 Forbidden on admin endpoints**
- Requires admin role
- Solution: Use admin credentials (admin/admin123)

**Model not found in prediction service**
- Training hasn't completed yet
- Solution: Wait for training or manually load model:
  ```bash
  curl -X POST http://localhost:5003/model/load
  ```

**MLflow connection refused**
- MLflow takes 30-60 seconds to initialize
- Solution: Wait and check logs:
  ```bash
  docker-compose logs mlflow
  ```

**Airflow DAG not triggering**
- Webserver not healthy
- Wrong credentials
- Solution: Verify Airflow at http://localhost:8081 and check `AIRFLOW_USER`/`AIRFLOW_PASS`

**Dashboard not loading**
- API Gateway not healthy
- Nginx not running
- Solution: Check service status:
  ```bash
  docker-compose ps
  make health
  ```

**Port already in use**
```bash
# Find process using port
lsof -i :8080  # macOS/Linux
netstat -ano | findstr :8080  # Windows

# Change port in docker-compose.yml
ports:
  - "8090:8080"  # Use 8090 instead
```

**Out of memory**
- Increase Docker memory limit (Docker Desktop settings)
- Recommended: At least 8GB RAM

**Prometheus/Grafana not showing data**
- Wait 30-60 seconds after startup
- Check Prometheus targets: http://localhost:9090/targets
- Verify service `/metrics` endpoints are accessible

### Health Check Commands

```bash
# All services
make health

# Individual services
curl http://localhost:8080/health  # API Gateway
curl http://localhost:5001/health  # Data Service
curl http://localhost:5002/health  # Training Service
curl http://localhost:5003/health  # Prediction Service
curl http://localhost:5004/health  # Auth Service

# Prometheus targets
curl http://localhost:9090/api/v1/targets
```

### Logs & Debugging

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f prediction_service

# Last 100 lines
docker-compose logs --tail=100 training_service

# Search logs
docker-compose logs | grep ERROR
```

---

## All Services Summary

| Service | Port | Container | Purpose |
|---------|------|-----------|---------|
| API Gateway | 8080 | api_gateway | Central routing & auth verification |
| Auth Service | 5004 | auth_service | User authentication & management |
| Data Service | 5001 | data_service | Data loading & preprocessing |
| Training Service | 5002 | training_service | Model training & MLflow logging |
| Prediction Service | 5003 | prediction_service | Single & batch inference |
| MLflow | 5000 | mlflow | Experiment tracking & model registry |
| Airflow Webserver | 8081 | airflow-webserver | DAG management UI |
| Airflow Scheduler | - | airflow-scheduler | DAG execution scheduler |
| Airflow DB | - | airflow-db | PostgreSQL metadata store |
| Web UI | 8082 | ui | Browser dashboard (Nginx) |
| Prometheus | 9090 | prometheus | Metrics collection |
| Grafana | 3000 | grafana | Metrics visualization |
| Airflow Init | - | airflow-init | Airflow initialization |

**Total**: 13 Docker containers

---

## Project Features

This project includes a complete MLOps implementation with the following capabilities:

- **Microservices Architecture**: 6 independent services (API Gateway, Auth, Data, Training, Prediction, UI)
- **Authentication & Authorization**: Role-based access control with admin and user roles
- **Workflow Orchestration**: Apache Airflow for automated model retraining
- **Experiment Tracking**: MLflow for tracking experiments and model registry
- **Data Versioning**: DVC for reproducible data and model versioning
- **Production Deployment**: 13 Docker containers with health checks and auto-restart
- **Real-time Monitoring**: Prometheus metrics collection from all services
- **Visualization Dashboards**: Pre-built Grafana dashboards for system monitoring
- **Complete REST API**: Token-authenticated endpoints for all operations
- **Comprehensive Testing**: Unit and integration tests for all components
- **ML Model**: LSTM text classifier for 27 product categories
- **NLP Pipeline**: French text preprocessing with lemmatization and stopword removal
- **Batch Processing**: Support for single and batch predictions
- **Health Monitoring**: Health check endpoints for all services

---

## Additional Documentation

- **MLFLOW_SETUP.md**: MLflow configuration details
- **DVC_SETUP.md**: DVC remote setup instructions
- **TESTING_GUIDE.md**: Testing procedures and guidelines
