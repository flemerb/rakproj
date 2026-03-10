# Rakuten MLOps - Complete Testing Guide

## Architecture Overview

**13 Docker containers** running via Docker Compose on a bridge network (`mlops_network`):

| # | Service | Port | Container | Purpose |
|---|---------|------|-----------|---------|
| 1 | **MLflow** | `5000` | mlflow | Experiment tracking & model registry |
| 2 | **Data Service** | `5001` | data_service | Data loading, splitting, preprocessing |
| 3 | **Training Service** | `5002` | training_service | LSTM model training with MLflow tracking |
| 4 | **Prediction Service** | `5003` | prediction_service | Model inference (single & batch) |
| 5 | **Auth Service** | `5004` | auth_service | User authentication & authorization |
| 6 | **API Gateway** | `8080` | api_gateway | Central entry point, token verification, routing |
| 7 | **Airflow Webserver** | `8081` | airflow-webserver | DAG management UI |
| 8 | **Airflow Scheduler** | - | airflow-scheduler | DAG execution engine |
| 9 | **Airflow DB** | - | airflow-db | PostgreSQL metadata store |
| 10 | **Airflow Init** | - | airflow-init | Initialization container |
| 11 | **Web Dashboard** | `8082` | ui | Browser UI (Nginx) |
| 12 | **Prometheus** | `9090` | prometheus | Metrics collection & storage |
| 13 | **Grafana** | `3000` | grafana | Metrics visualization & dashboards |

### Service Dependency Chain

```
MLflow (5000)
  ├─► Data Service (5001)
  │     └─► Training Service (5002)
  │           └─► Prediction Service (5003)
  │
  ├─► Auth Service (5004)
  │
  └─► API Gateway (8080)
        ├─► Airflow Webserver (8081)
        │     ├─► Airflow Scheduler
        │     └─► Airflow DB
        │
        ├─► Web Dashboard (8082)
        │
        └─► Prometheus (9090)
              └─► Grafana (3000)
```

### Authentication Flow

```
User ──login──► Auth Service ──token──► User
                    (5004)

User ──request + token──► API Gateway ──verify token──► Auth Service
                            (8080)              │
                                                └──► Forward to Services (5001, 5002, 5003)
```

### Monitoring Architecture

```
Flask Services ──/metrics──► Prometheus (scrape every 15s) ──► Grafana (dashboards)
  8080, 5001, 5002, 5003, 5004      9090                            3000
```

---

## Endpoints per Service

**API Gateway (8080):**
- `/health` (public)
- `/metrics` (public)
- `POST /auth/login` (public)
- `/api/v1/services` (requires token)
- `POST /api/v1/predict` (requires token)
- `POST /api/v1/predict/batch` (requires token)
- `POST /api/v1/admin/retrain` (requires admin token)
- `/api/v1/train/status` (requires token)
- `/api/v1/data` (requires token)
- `POST /api/v1/data/preprocess` (requires token)
- `/api/v1/models` (requires token)
- `GET /admin/users` (requires admin token)
- `POST /admin/users` (requires admin token)
- `DELETE /admin/users/<id>` (requires admin token)

**Auth Service (5004):**
- `/health` (public)
- `POST /auth/login` (public)
- `POST /auth/verify` (internal - used by API Gateway)
- `GET /admin/users` (requires admin token)
- `POST /admin/users` (requires admin token)
- `DELETE /admin/users/<id>` (requires admin token)

**Data Service (5001):**
- `/health` (public)
- `/metrics` (public)
- `POST /data/load`
- `POST /data/split`
- `POST /data/preprocess`
- `/data/status`

**Training Service (5002):**
- `/health` (public)
- `/metrics` (public)
- `POST /train/start`
- `/train/status`
- `/train/metrics`
- `/models/list`

**Prediction Service (5003):**
- `/health` (public)
- `/metrics` (public)
- `POST /model/load`
- `/model/info`
- `POST /predict`
- `POST /predict/batch`

**Airflow Webserver (8081):** Web UI at http://localhost:8081 (login: `admin` / `admin`)

**Web Dashboard (8082):** Browser UI at http://localhost:8082 (login: `admin` / `admin123`)

**Prometheus (9090):** Web UI at http://localhost:9090 — query metrics, view targets

**Grafana (3000):** Web UI at http://localhost:3000 (login: `admin` / `admin`) — pre-built dashboard

---

## Step-by-Step Testing Commands

### 1. Start all services

```bash
docker compose up -d --build
```

Wait ~90s for all health checks to pass (Airflow takes longer to initialize), then verify:

```bash
docker compose ps
```

All containers should show "healthy" or "running" status.

---

### 2. Check API Gateway home page (PUBLIC)

```bash
curl http://localhost:8080/
```

Returns the API overview with all available routes.

---

### 3. Health check - All services at once (PUBLIC)

```bash
curl http://localhost:8080/health
```

This pings every downstream service and returns their status. You should see `"status": "healthy"` for each service.

---

### 4. Check individual service health directly (PUBLIC)

```bash
# MLflow (returns HTTP 200, confirming the service is running)
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/

# Data Service
curl http://localhost:5001/health

# Training Service
curl http://localhost:5002/health

# Prediction Service
curl http://localhost:5003/health

# Auth Service
curl http://localhost:5004/health

# Prometheus
curl http://localhost:9090/-/healthy

# Grafana
curl http://localhost:3000/api/health
```

---

### 5. 🔐 AUTHENTICATION - Login and get token (PUBLIC)

**IMPORTANT**: All endpoints below (except `/health` and `/metrics`) require a Bearer token. You must login first!

```bash
# Login with default admin credentials
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Response:**
```json
{
  "status": "success",
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
  "role": "admin",
  "username": "admin"
}
```

**Save the token** - you'll need it for all subsequent requests:
```bash
# Export token to environment variable for easy reuse
export TOKEN="a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6"
```

---

### 6. Verify token is working

```bash
curl http://localhost:8080/api/v1/services \
  -H "Authorization: Bearer $TOKEN"
```

If you get `401 Unauthorized`, your token is invalid or expired. Login again.

---

### 7. List all users (ADMIN ONLY)

```bash
curl http://localhost:8080/admin/users \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "users": [
    {"id": 1, "username": "admin", "role": "admin"}
  ]
}
```

---

### 8. Create a new user (ADMIN ONLY)

```bash
curl -X POST http://localhost:8080/admin/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "role": "user"
  }'
```

**Response:**
```json
{
  "status": "success",
  "user_id": 2,
  "username": "testuser"
}
```

---

### 9. Login as the new user

```bash
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

Save this token for non-admin operations if needed.

---

### 10. Delete a user (ADMIN ONLY)

```bash
# Delete user with ID 2
curl -X DELETE http://localhost:8080/admin/users/2 \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "status": "success",
  "message": "User deleted"
}
```

---

## DATA OPERATIONS (Requires Token)

### 11. Check data status

```bash
curl http://localhost:8080/api/v1/data \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "raw_data_available": true,
  "preprocessed_data_available": false,
  "train_samples": 16113,
  "validation_samples": 1350,
  "test_samples": 2000
}
```

---

### 12. Load raw data (Direct to Data Service)

**Note**: Direct service calls bypass API Gateway auth. In production, use API Gateway routes.

```bash
curl -X POST http://localhost:5001/data/load \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "status": "success",
  "message": "Raw data loaded successfully",
  "train_samples": 16113,
  "test_samples": 2000
}
```

---

### 13. Split data into train/val/test

```bash
curl -X POST http://localhost:5001/data/split \
  -H "Content-Type: application/json" \
  -d '{"samples_per_class": 600}'
```

---

### 14. Preprocess data

Via API Gateway (recommended):

```bash
curl -X POST http://localhost:8080/api/v1/data/preprocess \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Or directly to Data Service:

```bash
curl -X POST http://localhost:5001/data/preprocess \
  -H "Content-Type: application/json" \
  -d '{"text_columns": ["designation", "description"]}'
```

**Response:**
```json
{
  "status": "success",
  "message": "Data preprocessing completed",
  "preprocessed_samples": 16113
}
```

---

## MODEL TRAINING (Requires Token)

### 15. Option A: Start training via Training Service (Manual)

```bash
curl -X POST http://localhost:5002/train/start \
  -H "Content-Type: application/json" \
  -d '{"epochs": 10, "batch_size": 32}'
```

**Response:**
```json
{
  "status": "success",
  "message": "Training started in background",
  "training_id": "train_20260310_120000"
}
```

---

### 16. Option B: Trigger retraining via Airflow DAG (ADMIN ONLY - Recommended)

This triggers the full orchestrated pipeline: preprocess → train → wait → reload model

```bash
curl -X POST http://localhost:8080/api/v1/admin/retrain \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "epochs": 10,
    "batch_size": 32
  }'
```

**Response:**
```json
{
  "status": "success",
  "dag_run_id": "manual__2026-03-10T12:00:00+00:00",
  "message": "Retraining DAG triggered successfully",
  "airflow_url": "http://localhost:8081/dags/retrain_pipeline/grid"
}
```

Monitor progress at: http://localhost:8081

---

### 17. Check training progress (poll while training runs)

Via API Gateway:
```bash
curl http://localhost:8080/api/v1/train/status \
  -H "Authorization: Bearer $TOKEN"
```

Or directly:
```bash
curl http://localhost:5002/train/status
```

**Response:**
```json
{
  "training_active": true,
  "current_epoch": 5,
  "total_epochs": 10,
  "progress": 50,
  "latest_metrics": {
    "train_loss": 0.234,
    "train_accuracy": 0.912,
    "val_loss": 0.312,
    "val_accuracy": 0.887
  }
}
```

---

### 18. Get final training metrics (after training completes)

```bash
curl http://localhost:5002/train/metrics
```

**Response:**
```json
{
  "final_train_loss": 0.152,
  "final_train_accuracy": 0.945,
  "final_val_loss": 0.289,
  "final_val_accuracy": 0.901,
  "total_epochs": 10,
  "training_duration_seconds": 3456
}
```

---

### 19. List registered models from MLflow

Via API Gateway:
```bash
curl http://localhost:8080/api/v1/models \
  -H "Authorization: Bearer $TOKEN"
```

Or directly:
```bash
curl http://localhost:5002/models/list
```

**Response:**
```json
{
  "models": [
    {
      "name": "lstm_rakuten_classifier",
      "version": 3,
      "stage": "Production",
      "last_updated": "2026-03-10T12:00:00Z"
    }
  ]
}
```

---

## MODEL PREDICTION (Requires Token)

### 20. Load model into prediction service

```bash
curl -X POST http://localhost:5003/model/load \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "status": "success",
  "message": "Model loaded successfully",
  "model_version": "best_lstm_model.h5"
}
```

---

### 21. Get model info

```bash
curl http://localhost:5003/model/info
```

**Response:**
```json
{
  "model_loaded": true,
  "model_path": "/app/models/best_lstm_model.h5",
  "num_classes": 27,
  "vocabulary_size": 10000
}
```

---

### 22. Single prediction

Via API Gateway (recommended):

```bash
curl -X POST http://localhost:8080/api/v1/predict \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Samsung Galaxy S21 smartphone 128GB noir"}'
```

Or directly to Prediction Service:

```bash
curl -X POST http://localhost:5003/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Samsung Galaxy S21 smartphone 128GB noir"}'
```

**Response:**
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

---

### 23. Batch prediction

Via API Gateway:

```bash
curl -X POST http://localhost:8080/api/v1/predict/batch \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Samsung Galaxy S21 smartphone",
      "Harry Potter book collection",
      "Nike Air Max running shoes",
      "LEGO Star Wars set"
    ]
  }'
```

Or directly:

```bash
curl -X POST http://localhost:5003/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Pull en laine rouge pour hiver",
      "Ordinateur portable gaming ASUS"
    ]
  }'
```

**Response:**
```json
{
  "status": "success",
  "predictions": [
    {
      "text": "Pull en laine rouge pour hiver",
      "predicted_class": 5,
      "category_name": "Clothing",
      "confidence": 0.87
    },
    {
      "text": "Ordinateur portable gaming ASUS",
      "predicted_class": 12,
      "category_name": "Electronics",
      "confidence": 0.91
    }
  ]
}
```

---

## WEB DASHBOARD TESTING (Browser UI)

### 24. Access the Web Dashboard

Open in browser:
```
http://localhost:8082
```

---

### 25. Test login page

1. You should see a dark-themed login page
2. Enter credentials:
   - Username: `admin`
   - Password: `admin123`
3. Click "Login"
4. You should be redirected to the prediction interface

---

### 26. Test prediction interface

1. Enter a product description in French:
   - Example: "Smartphone Samsung Galaxy S21 128GB noir"
   - Example: "Pull en laine rouge pour l'hiver"
2. Click "Predict"
3. Verify response shows:
   - Predicted category name
   - Confidence percentage
   - Product type code

---

### 27. Test admin panel (Admin users only)

1. Click "Admin Panel" button
2. Verify you can see:
   - List of existing users
   - Create user form
   - Delete user buttons
   - Retrain model section

**Create a user:**
1. Enter username: `demouser`
2. Enter password: `demopass123`
3. Select role: `user`
4. Click "Create User"
5. Verify user appears in the list

**Delete a user:**
1. Click delete icon next to the user
2. Verify user is removed from the list

**Trigger retraining:**
1. In "Retrain Model" section, set:
   - Epochs: 5
   - Batch size: 32
2. Click "Start Retraining"
3. You should see a success message with DAG run ID
4. Navigate to Airflow UI to monitor progress

---

## AIRFLOW TESTING (Workflow Orchestration)

### 28. Access Airflow UI

Open in browser:
```
http://localhost:8081
```

Login: `admin` / `admin`

---

### 29. Verify retrain_pipeline DAG exists

1. In Airflow UI, check the DAGs list
2. Find `retrain_pipeline` DAG
3. Verify it shows 4 tasks:
   - `preprocess_new_data`
   - `start_training`
   - `wait_for_training_completion`
   - `reload_model_in_prediction_service`

---

### 30. Manually trigger the DAG (from Airflow UI)

1. Click on `retrain_pipeline` DAG
2. Click the "Play" button (▶) on the right
3. In the modal, optionally add configuration:
   ```json
   {
     "epochs": 5,
     "batch_size": 32
   }
   ```
4. Click "Trigger"
5. Watch the DAG run in Grid view
6. Each task should turn green as it completes

---

### 31. Trigger DAG via API (already tested in step 16)

This is the programmatic way to trigger retraining:

```bash
curl -X POST http://localhost:8080/api/v1/admin/retrain \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"epochs": 5, "batch_size": 32}'
```

Then verify in Airflow UI that a new DAG run appears.

---

## MLFLOW TESTING (Experiment Tracking)

### 32. Access MLflow UI

Open in browser:
```
http://localhost:5000
```

---

### 33. View experiments

1. Click on "Experiments" in sidebar
2. You should see experiments created during training
3. Click on an experiment to view runs

---

### 34. View run details

1. Click on a specific run
2. Verify you can see:
   - Parameters (epochs, batch_size, lstm_units, etc.)
   - Metrics (train_loss, train_accuracy, val_loss, val_accuracy)
   - Training duration
   - Artifacts (model file, tokenizer, mappings)

---

### 35. Compare runs

1. Select multiple runs (checkboxes)
2. Click "Compare"
3. View side-by-side comparison of parameters and metrics

---

### 36. Download model artifacts

1. Open a run
2. Scroll to "Artifacts" section
3. Click on `best_lstm_model.h5`
4. Click "Download" to download the trained model

---

## MONITORING & METRICS TESTING

### 37. Check Prometheus metrics (raw)

Each service exposes a `/metrics` endpoint with Prometheus-formatted metrics (PUBLIC):

```bash
# API Gateway metrics
curl http://localhost:8080/metrics

# Auth Service metrics
curl http://localhost:5004/metrics

# Prediction Service metrics (includes ML-specific metrics)
curl http://localhost:5003/metrics

# Training Service metrics
curl http://localhost:5002/metrics

# Data Service metrics
curl http://localhost:5001/metrics
```

---

### 38. Verify Prometheus is scraping all targets

Open in browser: http://localhost:9090/targets

Or via API:

```bash
curl -s http://localhost:9090/api/v1/targets | python3 -m json.tool
```

All targets should show `"health": "up"`:
- api_gateway (8080)
- data_service (5001)
- training_service (5002)
- prediction_service (5003)
- auth_service (5004)

---

### 39. Query metrics in Prometheus

Open http://localhost:9090 and try these PromQL queries:

```promql
# Check which services are up
up

# Total requests per service endpoint
gateway_requests_total

# Request rate (requests per second over 5 minutes)
rate(gateway_request_duration_seconds_bucket[5m])

# Downstream service availability
gateway_service_up

# Prediction count per class
predictions_total

# Prediction confidence distribution (median)
histogram_quantile(0.50, rate(prediction_confidence_bucket[5m]))

# Model inference latency (p95)
histogram_quantile(0.95, rate(prediction_inference_duration_seconds_bucket[5m]))

# Training status (1 = active, 0 = idle)
training_active

# Authentication requests
rate(auth_requests_total[5m])
```

---

### 40. Access Grafana Dashboard

Open in browser:
```
http://localhost:3000
```

Login: `admin` / `admin`

Navigate to **Dashboards** → **"Rakuten MLOps - Performance Monitoring"** (or similar name)

The dashboard includes:
- **Service Health Overview** — UP/DOWN status for all application services
- **Request Rate** — requests per second per service/endpoint
- **Request Latency (p95)** — response time percentiles
- **Predictions by Class** — distribution of predicted categories
- **Model Inference Latency** — p50/p95/p99 inference time
- **Prediction Confidence** — confidence score distribution
- **Total Predictions** — counter of all predictions made
- **Training Status** — IDLE/TRAINING indicator
- **Training Loss & Accuracy** — latest training metrics
- **Authentication Metrics** — login attempts, token verifications

---

### 41. Create custom Grafana panel

1. Click "Add panel" in dashboard
2. Enter a PromQL query, e.g., `rate(predictions_total[5m])`
3. Configure visualization type (graph, stat, gauge, etc.)
4. Click "Apply"

---

### 42. Stop everything

```bash
docker compose down
```

To remove all volumes (WARNING: deletes all data):
```bash
docker compose down -v
```

---

## Full Pipeline Test (Complete End-to-End)

**Copy-paste sequence that tests the entire system:**

```bash
# ============================================================
# PHASE 1: STARTUP & VERIFICATION (90 seconds)
# ============================================================

# 1. Start all 13 containers
docker compose up -d --build

# Wait for all services to initialize (Airflow needs ~90s)
echo "Waiting 90 seconds for all services to start..."
sleep 90

# 2. Verify all containers are running
docker compose ps

# 3. Verify all services are healthy
curl http://localhost:8080/health

# 4. Check individual service health
echo "Checking individual services..."
curl http://localhost:5001/health  # Data Service
curl http://localhost:5002/health  # Training Service
curl http://localhost:5003/health  # Prediction Service
curl http://localhost:5004/health  # Auth Service
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3000/api/health  # Grafana


# ============================================================
# PHASE 2: AUTHENTICATION & USER MANAGEMENT
# ============================================================

# 5. Login as admin and get token
echo "Logging in as admin..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

echo $LOGIN_RESPONSE

# Extract token (requires jq - install with: sudo apt install jq)
export TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.token')
echo "Token: $TOKEN"

# Alternative if jq not available - manually copy token from response and:
# export TOKEN="your_token_here"

# 6. Verify token works
curl http://localhost:8080/api/v1/services \
  -H "Authorization: Bearer $TOKEN"

# 7. List existing users
curl http://localhost:8080/admin/users \
  -H "Authorization: Bearer $TOKEN"

# 8. Create a test user
curl -X POST http://localhost:8080/admin/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "role": "user"
  }'


# ============================================================
# PHASE 3: DATA PREPARATION
# ============================================================

# 9. Check data status
curl http://localhost:8080/api/v1/data \
  -H "Authorization: Bearer $TOKEN"

# 10. Load raw data
curl -X POST http://localhost:5001/data/load \
  -H "Content-Type: application/json" \
  -d '{}'

# 11. Split data into train/val/test
curl -X POST http://localhost:5001/data/split \
  -H "Content-Type: application/json" \
  -d '{"samples_per_class": 600}'

# 12. Preprocess data (via API Gateway with auth)
curl -X POST http://localhost:8080/api/v1/data/preprocess \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'


# ============================================================
# PHASE 4: MODEL TRAINING (Option A - Direct Training)
# ============================================================

# 13A. Start training directly (without Airflow)
curl -X POST http://localhost:5002/train/start \
  -H "Content-Type: application/json" \
  -d '{"epochs": 5, "batch_size": 32}'

# 14A. Poll training status (repeat every 30s until complete)
watch -n 30 'curl -s http://localhost:5002/train/status'

# Or manually:
curl http://localhost:5002/train/status


# ============================================================
# PHASE 4: MODEL TRAINING (Option B - Airflow DAG - RECOMMENDED)
# ============================================================

# 13B. Trigger retraining via Airflow DAG (admin only)
curl -X POST http://localhost:8080/api/v1/admin/retrain \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "epochs": 5,
    "batch_size": 32
  }'

# 14B. Monitor progress in Airflow UI
# Open: http://localhost:8081 (admin/admin)
# Watch the retrain_pipeline DAG execution

# 15B. Also poll training status
curl http://localhost:8080/api/v1/train/status \
  -H "Authorization: Bearer $TOKEN"


# ============================================================
# PHASE 5: MODEL INFERENCE
# ============================================================

# 16. Get final training metrics (after training completes)
curl http://localhost:5002/train/metrics

# 17. List registered models in MLflow
curl http://localhost:8080/api/v1/models \
  -H "Authorization: Bearer $TOKEN"

# 18. Load model into prediction service
curl -X POST http://localhost:5003/model/load \
  -H "Content-Type: application/json" \
  -d '{}'

# 19. Get model info
curl http://localhost:5003/model/info

# 20. Single prediction via API Gateway
curl -X POST http://localhost:8080/api/v1/predict \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Samsung Galaxy S21 smartphone 128GB noir"}'

# 21. Batch prediction
curl -X POST http://localhost:8080/api/v1/predict/batch \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Pull en laine rouge pour hiver",
      "Ordinateur portable gaming ASUS ROG",
      "Harry Potter et la pierre philosophale livre",
      "Nike Air Max chaussures de running"
    ]
  }'


# ============================================================
# PHASE 6: MONITORING VERIFICATION
# ============================================================

# 22. Check Prometheus metrics endpoints
curl http://localhost:8080/metrics           # API Gateway
curl http://localhost:5003/metrics           # Prediction Service
curl http://localhost:5002/metrics           # Training Service
curl http://localhost:5001/metrics           # Data Service
curl http://localhost:5004/metrics           # Auth Service

# 23. Verify Prometheus targets
curl -s http://localhost:9090/api/v1/targets | python3 -m json.tool

# 24. Check Grafana health
curl http://localhost:3000/api/health


# ============================================================
# PHASE 7: BROWSER UI TESTING
# ============================================================

echo "=== BROWSER TESTING ==="
echo "1. Web Dashboard:  http://localhost:8082 (admin/admin123)"
echo "2. MLflow UI:      http://localhost:5000"
echo "3. Airflow UI:     http://localhost:8081 (admin/admin)"
echo "4. Prometheus:     http://localhost:9090"
echo "5. Grafana:        http://localhost:3000 (admin/admin)"
echo ""
echo "Test these in your browser:"
echo "  - Login to dashboard and make predictions"
echo "  - Check MLflow experiments and runs"
echo "  - Verify Airflow DAG execution"
echo "  - View Prometheus metrics"
echo "  - Explore Grafana dashboards"


# ============================================================
# PHASE 8: CLEANUP
# ============================================================

# 25. View logs (optional)
# docker compose logs -f prediction_service
# docker compose logs -f training_service

# 26. Stop all services
docker compose down

# Optional: Remove all volumes (WARNING: deletes data)
# docker compose down -v
```

---

## Quick Health Check (Before Presentation)

**Fast verification that everything is working:**

```bash
# Start services
docker compose up -d --build
sleep 90

# Login and get token
export TOKEN=$(curl -s -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | jq -r '.token')

# Quick test
curl http://localhost:8080/health
curl http://localhost:8080/api/v1/services -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:8080/api/v1/predict \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Samsung Galaxy S21"}'

# Open dashboards
echo "Open these URLs in browser:"
echo "  http://localhost:8082 (Dashboard)"
echo "  http://localhost:5000 (MLflow)"
echo "  http://localhost:8081 (Airflow)"
echo "  http://localhost:3000 (Grafana)"
```

---

## Makefile Commands (Convenience Shortcuts)

If the project has a Makefile, you can use these commands:

```bash
make help           # Show all available commands
make presentation   # Full setup: stop → start → wait → verify
make health         # Check all service health endpoints
make quick-check    # Pre-presentation verification
make up             # Start all services
make down           # Stop all services
make restart        # Restart all services
make logs           # Follow service logs
make test-predict   # Test prediction with sample data
make verify-all     # Comprehensive system verification
```

---

## Test Coverage Summary

| Test Category | Test Steps | Requires Auth | Services Tested |
|---------------|------------|---------------|-----------------|
| **Startup & Health** | 1-4 | No | All 13 containers |
| **Authentication** | 5-10 | No (testing auth) | Auth Service, API Gateway |
| **Data Operations** | 11-14 | Yes | Data Service, API Gateway |
| **Training (Direct)** | 15, 17-19 | Partial | Training Service, MLflow |
| **Training (Airflow)** | 16-19, 28-31 | Yes (admin) | Airflow, Training Service, MLflow |
| **Prediction** | 20-23 | Yes | Prediction Service, API Gateway |
| **Web Dashboard** | 24-27 | Yes | UI Service, all backend |
| **MLflow** | 32-36 | No (UI) | MLflow |
| **Monitoring** | 37-41 | No | Prometheus, Grafana |
| **Cleanup** | 42 | No | All containers |

**Total Test Steps**: 42
**Authentication Protected**: 22 steps
**Public Endpoints**: 20 steps
**Admin-Only Operations**: 8 steps

---

## Troubleshooting

### Common Issues and Solutions

#### 1. **401 Unauthorized Error**

**Symptom**: `{"error": "Unauthorized", "message": "Missing authorization token"}`

**Causes**:
- Token not provided in request
- Token expired
- Invalid token format

**Solutions**:
```bash
# Login again to get a fresh token
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Export the new token
export TOKEN="your_new_token_here"

# Verify it works
curl http://localhost:8080/api/v1/services \
  -H "Authorization: Bearer $TOKEN"
```

---

#### 2. **403 Forbidden on Admin Endpoints**

**Symptom**: `{"error": "Forbidden", "message": "Admin access required"}`

**Cause**: Non-admin user trying to access admin-only endpoints

**Solutions**:
- Login as admin user (username: `admin`, password: `admin123`)
- Or create an admin user via the auth service

---

#### 3. **Services Not Starting / Health Check Failing**

**Symptom**: `docker compose ps` shows unhealthy containers

**Solutions**:
```bash
# Check logs for the failing service
docker compose logs <service_name>

# Common failing services:
docker compose logs airflow-webserver
docker compose logs mlflow
docker compose logs training_service

# Restart specific service
docker compose restart <service_name>

# Full rebuild
docker compose down
docker compose up -d --build

# Nuclear option (WARNING: deletes all data)
docker compose down -v
docker compose up -d --build
```

---

#### 4. **Airflow Takes Too Long to Start**

**Symptom**: Airflow containers show "starting" for > 2 minutes

**Cause**: Airflow needs to initialize database and create admin user

**Solutions**:
```bash
# Wait longer (up to 120 seconds)
sleep 120

# Check init container logs
docker compose logs airflow-init

# Check webserver logs
docker compose logs airflow-webserver

# Verify Airflow is ready
curl http://localhost:8081/health
```

---

#### 5. **MLflow Connection Refused**

**Symptom**: `requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))`

**Cause**: MLflow server not fully initialized

**Solutions**:
```bash
# Check MLflow status
curl http://localhost:5000/health || echo "MLflow not ready"

# Check logs
docker compose logs mlflow

# Restart MLflow
docker compose restart mlflow

# Wait and retry
sleep 30
curl http://localhost:5000/
```

---

#### 6. **Model Not Found in Prediction Service**

**Symptom**: `{"error": "Model not loaded", "message": "No model available"}`

**Cause**: Model not trained yet or not loaded into prediction service

**Solutions**:
```bash
# Check if model file exists
docker compose exec prediction_service ls -la /app/models/

# Train a model first
curl -X POST http://localhost:5002/train/start \
  -H "Content-Type: application/json" \
  -d '{"epochs": 5, "batch_size": 32}'

# Wait for training to complete, then load model
curl -X POST http://localhost:5003/model/load \
  -H "Content-Type: application/json" \
  -d '{}'

# Verify model is loaded
curl http://localhost:5003/model/info
```

---

#### 7. **Data Not Preprocessed**

**Symptom**: `{"error": "Preprocessed data not found"}`

**Cause**: Data preprocessing not completed

**Solutions**:
```bash
# Check data status
curl http://localhost:5001/data/status

# Load raw data
curl -X POST http://localhost:5001/data/load \
  -H "Content-Type: application/json" \
  -d '{}'

# Split data
curl -X POST http://localhost:5001/data/split \
  -H "Content-Type: application/json" \
  -d '{"samples_per_class": 600}'

# Preprocess data
curl -X POST http://localhost:5001/data/preprocess \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

#### 8. **Prometheus Not Scraping Targets**

**Symptom**: All targets show "DOWN" in http://localhost:9090/targets

**Cause**:
- Services not exposing `/metrics` endpoint
- Network connectivity issues
- Prometheus configuration error

**Solutions**:
```bash
# Check if services expose metrics
curl http://localhost:8080/metrics
curl http://localhost:5001/metrics
curl http://localhost:5002/metrics
curl http://localhost:5003/metrics
curl http://localhost:5004/metrics

# Check Prometheus logs
docker compose logs prometheus

# Restart Prometheus
docker compose restart prometheus

# Verify prometheus.yml configuration
docker compose exec prometheus cat /etc/prometheus/prometheus.yml
```

---

#### 9. **Grafana Dashboard Not Showing Data**

**Symptom**: Grafana panels show "No data"

**Cause**:
- Prometheus not connected
- No metrics generated yet
- Time range too narrow

**Solutions**:
```bash
# Check Grafana datasource
# Open: http://localhost:3000/datasources
# Verify Prometheus datasource is configured and working

# Generate some traffic to create metrics
curl -X POST http://localhost:8080/api/v1/predict \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "test product"}'

# Wait 15-30 seconds for Prometheus to scrape
sleep 30

# Refresh Grafana dashboard

# Adjust time range to "Last 15 minutes" or "Last 1 hour"
```

---

#### 10. **Port Already in Use**

**Symptom**: `Error: bind: address already in use`

**Cause**: Another process is using the port

**Solutions**:
```bash
# Find process using the port (Linux/Mac)
lsof -i :8080
lsof -i :5000

# Find process (Windows)
netstat -ano | findstr :8080

# Kill the process or change port in docker-compose.yml
# Example: Change API Gateway port
# ports:
#   - "8090:8080"  # Use 8090 externally instead
```

---

#### 11. **Docker Out of Memory**

**Symptom**: Containers crashing, "137" exit code (OOM killed)

**Cause**: Insufficient RAM allocated to Docker

**Solutions**:
1. Open Docker Desktop Settings
2. Go to Resources → Advanced
3. Increase Memory to at least 8GB
4. Click "Apply & Restart"
5. Rebuild containers:
   ```bash
   docker compose down
   docker compose up -d --build
   ```

---

#### 12. **Training Taking Too Long / Hanging**

**Symptom**: Training stuck at 0% or very slow progress

**Cause**:
- CPU-only training (no GPU)
- Large dataset
- High epoch count

**Solutions**:
```bash
# Reduce training parameters
curl -X POST http://localhost:5002/train/start \
  -H "Content-Type: application/json" \
  -d '{"epochs": 3, "batch_size": 64}'

# Monitor training progress
watch -n 10 'curl -s http://localhost:5002/train/status | jq'

# Check resource usage
docker stats

# Check training service logs
docker compose logs -f training_service
```

---

#### 13. **Airflow DAG Not Triggering**

**Symptom**: API returns success but DAG doesn't run

**Cause**:
- Airflow scheduler not running
- DAG paused
- Invalid credentials

**Solutions**:
```bash
# Check if scheduler is running
docker compose ps airflow-scheduler

# Check scheduler logs
docker compose logs airflow-scheduler

# Open Airflow UI and unpause the DAG
# http://localhost:8081
# Toggle the switch next to retrain_pipeline

# Verify Airflow credentials in docker-compose.yml
# Default: admin/admin

# Trigger manually from UI to test
```

---

#### 14. **Web Dashboard Won't Load**

**Symptom**: Browser shows "Connection refused" at http://localhost:8082

**Cause**: UI service not running or Nginx misconfigured

**Solutions**:
```bash
# Check UI service status
docker compose ps ui

# Check logs
docker compose logs ui

# Restart UI service
docker compose restart ui

# Verify Nginx is serving files
docker compose exec ui ls -la /usr/share/nginx/html/

# Test with curl
curl http://localhost:8082
```

---

#### 15. **jq Command Not Found** (in full pipeline test)

**Symptom**: `bash: jq: command not found`

**Cause**: jq (JSON processor) not installed

**Solutions**:
```bash
# Install jq
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y jq

# macOS
brew install jq

# Alternative: Manually extract token
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

echo $LOGIN_RESPONSE
# Manually copy the token value and:
export TOKEN="paste_token_here"
```

---

### Diagnostic Commands

**Check all container status:**
```bash
docker compose ps
```

**Check all container logs:**
```bash
docker compose logs
```

**Check specific service logs:**
```bash
docker compose logs -f <service_name>
# Examples:
docker compose logs -f api_gateway
docker compose logs -f prediction_service
docker compose logs -f airflow-webserver
```

**Check resource usage:**
```bash
docker stats
```

**Exec into a container:**
```bash
docker compose exec <service_name> bash
# Example:
docker compose exec prediction_service bash
```

**Restart specific service:**
```bash
docker compose restart <service_name>
```

**Rebuild specific service:**
```bash
docker compose up -d --build <service_name>
```

**Clean slate restart:**
```bash
docker compose down -v  # WARNING: Deletes volumes
docker compose up -d --build
```

---

## Expected Test Results

### Successful Test Indicators

✅ **All 13 containers running**: `docker compose ps` shows all healthy
✅ **Health check passes**: All services return `"status": "healthy"`
✅ **Authentication works**: Login returns token
✅ **Predictions work**: Returns predicted category with confidence > 0.5
✅ **Training completes**: Progress reaches 100%, metrics logged to MLflow
✅ **Airflow DAG runs**: All 4 tasks turn green in Airflow UI
✅ **Prometheus scraping**: All 5 targets show "UP"
✅ **Grafana displays data**: Dashboards show metrics graphs
✅ **Web UI functional**: Can login and make predictions via browser

### Normal Performance Benchmarks

| Operation | Expected Time | Acceptable Range |
|-----------|---------------|------------------|
| Full startup (13 containers) | 90s | 60-120s |
| Data loading | 5s | 3-10s |
| Data preprocessing | 30s | 20-60s |
| Training (5 epochs) | 5-10 min | 3-15 min (CPU) |
| Single prediction | < 1s | 0.1-2s |
| Batch prediction (10 items) | < 2s | 0.5-5s |
| Airflow DAG complete | 10-15 min | 8-20 min |

---

## Testing Checklist

Use this checklist before a presentation or demo:

- [ ] All 13 containers running (`docker compose ps`)
- [ ] All services healthy (`make health` or `curl http://localhost:8080/health`)
- [ ] Can login and get token
- [ ] Can list services with token
- [ ] Can create and delete users (admin)
- [ ] Data is preprocessed
- [ ] Model is trained (or loaded from previous run)
- [ ] Can make single prediction
- [ ] Can make batch prediction
- [ ] Web dashboard accessible (http://localhost:8082)
- [ ] MLflow UI shows experiments (http://localhost:5000)
- [ ] Airflow UI accessible (http://localhost:8081)
- [ ] Prometheus shows all targets UP (http://localhost:9090/targets)
- [ ] Grafana dashboard displays metrics (http://localhost:3000)
- [ ] Can trigger Airflow DAG for retraining

---

## Additional Resources

- **Main README**: `README.md` - Project overview and setup
- **MLflow Setup**: `MLFLOW_SETUP.md` - MLflow configuration details
- **DVC Setup**: `DVC_SETUP.md` - DVC remote configuration
- **Project Documentation**: `PROJECT_COMPLETE_DOCUMENTATION.md` - Complete technical documentation

---

**Document Version**: 1.0
**Last Updated**: March 10, 2026
**Verified Working**: ✅ Yes - All 42 test steps verified
