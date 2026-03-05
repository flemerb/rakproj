# Rakuten MLOps - Microservices Architecture & Testing Guide

## Architecture Overview

**7 services** running via Docker Compose on a bridge network (`mlops_network`):

| # | Service | Port | Purpose |
|---|---------|------|---------|
| 1 | **MLflow** | `5000` | Experiment tracking & model registry |
| 2 | **Data Service** | `5001` | Data loading, splitting, preprocessing |
| 3 | **Training Service** | `5002` | LSTM model training with MLflow tracking |
| 4 | **Prediction Service** | `5003` | Model inference (single & batch) |
| 5 | **API Gateway** | `8080` | Central entry point, routes to all services |
| 6 | **Prometheus** | `9090` | Metrics collection & storage |
| 7 | **Grafana** | `3000` | Metrics visualization & dashboards |

### Service Dependency Chain

```
MLflow (5000)
  └─► Data Service (5001)
        └─► Training Service (5002)
              └─► Prediction Service (5003)
                    └─► API Gateway (8080)
                          └─► Prometheus (9090) ──► Grafana (3000)
```

### Monitoring Architecture

```
Flask Services ──/metrics──► Prometheus (scrape every 15s) ──► Grafana (dashboards)
  8080, 5001, 5002, 5003          9090                            3000
```

---

## Endpoints per Service

**API Gateway (8080):** `/`, `/health`, `/metrics`, `/api/v1/services`, `/api/v1/predict`, `/api/v1/predict/batch`, `/api/v1/train`, `/api/v1/train/status`, `/api/v1/data`, `/api/v1/data/preprocess`, `/api/v1/models`

**Data Service (5001):** `/health`, `/metrics`, `/data/load`, `/data/split`, `/data/preprocess`, `/data/status`

**Training Service (5002):** `/health`, `/metrics`, `/train/start`, `/train/status`, `/train/metrics`, `/models/list`

**Prediction Service (5003):** `/health`, `/metrics`, `/model/load`, `/model/info`, `/predict`, `/predict/batch`

**Prometheus (9090):** Web UI at http://localhost:9090 — query metrics, view targets

**Grafana (3000):** Web UI at http://localhost:3000 (login: `admin` / `admin`) — pre-built dashboard

---

## Step-by-Step Testing Commands

### 1. Start all services

```bash
docker-compose up -d --build
```

Wait ~30s for all health checks to pass, then verify:

```bash
docker-compose ps
```

---

### 2. Check API Gateway home page

```bash
curl http://localhost:8080/
```

Returns the API overview with all available routes.

---

### 3. Health check (all services at once)

```bash
curl http://localhost:8080/health
```

This pings every downstream service and returns their status. You should see `"status": "healthy"` for each.

---

### 4. List all available services and endpoints

```bash
curl http://localhost:8080/api/v1/services
```

---

### 5. Check individual service health directly

```bash
# MLflow
curl http://localhost:5000/health

# Data Service
curl http://localhost:5001/health

# Training Service
curl http://localhost:5002/health

# Prediction Service
curl http://localhost:5003/health
```

---

### 6. Check data status

```bash
curl http://localhost:8080/api/v1/data
```

Or directly:

```bash
curl http://localhost:5001/data/status
```

---

### 7. Load raw data

```bash
curl -X POST http://localhost:5001/data/load \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

### 8. Split data into train/val/test

```bash
curl -X POST http://localhost:5001/data/split \
  -H "Content-Type: application/json" \
  -d '{"samples_per_class": 600}'
```

---

### 9. Preprocess data

Via API Gateway:

```bash
curl -X POST http://localhost:8080/api/v1/data/preprocess \
  -H "Content-Type: application/json" \
  -d '{"text_columns": ["designation", "description"]}'
```

Or directly:

```bash
curl -X POST http://localhost:5001/data/preprocess \
  -H "Content-Type: application/json" \
  -d '{"text_columns": ["designation", "description"]}'
```

---

### 10. Start model training

Via API Gateway:

```bash
curl -X POST http://localhost:8080/api/v1/train \
  -H "Content-Type: application/json" \
  -d '{"epochs": 10, "batch_size": 32}'
```

Or directly:

```bash
curl -X POST http://localhost:5002/train/start \
  -H "Content-Type: application/json" \
  -d '{"epochs": 10, "batch_size": 32}'
```

---

### 11. Check training progress (poll while training runs)

```bash
curl http://localhost:8080/api/v1/train/status
```

Or directly:

```bash
curl http://localhost:5002/train/status
```

Returns `is_training`, `progress` (0-100), `current_epoch`, and live metrics.

---

### 12. Get final training metrics (after training completes)

```bash
curl http://localhost:5002/train/metrics
```

---

### 13. List registered models from MLflow

```bash
curl http://localhost:8080/api/v1/models
```

Or directly:

```bash
curl http://localhost:5002/models/list
```

---

### 14. Load model into prediction service

```bash
curl -X POST http://localhost:5003/model/load \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

### 15. Get model info

```bash
curl http://localhost:5003/model/info
```

---

### 16. Single prediction

Via API Gateway:

```bash
curl -X POST http://localhost:8080/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Samsung Galaxy S21 smartphone"}'
```

Or directly:

```bash
curl -X POST http://localhost:5003/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Samsung Galaxy S21 smartphone"}'
```

---

### 17. Batch prediction

Via API Gateway:

```bash
curl -X POST http://localhost:8080/api/v1/predict/batch \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Samsung Galaxy S21 smartphone", "Harry Potter book collection", "Nike Air Max running shoes", "LEGO Star Wars set"]}'
```

Or directly:

```bash
curl -X POST http://localhost:5003/predict/batch \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Samsung Galaxy S21 smartphone", "Harry Potter book collection", "Nike Air Max running shoes"]}'
```

---

### 18. Access MLflow UI

Open in browser:

```
http://localhost:5000
```

---

### 19. Check Prometheus metrics (raw)

Each service exposes a `/metrics` endpoint with Prometheus-formatted metrics:

```bash
# API Gateway metrics
curl http://localhost:8080/metrics

# Prediction Service metrics (includes ML-specific metrics)
curl http://localhost:5003/metrics

# Training Service metrics
curl http://localhost:5002/metrics

# Data Service metrics
curl http://localhost:5001/metrics
```

---

### 20. Verify Prometheus is scraping all targets

Open in browser: http://localhost:9090/targets

Or via API:

```bash
curl -s http://localhost:9090/api/v1/targets | python3 -m json.tool
```

All 5 targets (api_gateway, data_service, training_service, prediction_service, prometheus) should show `"health": "up"`.

---

### 21. Query metrics in Prometheus

Open http://localhost:9090 and try these PromQL queries:

```
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
```

---

### 22. Access Grafana Dashboard

Open in browser:

```
http://localhost:3000
```

Login: `admin` / `admin`

Navigate to **Dashboards** → **"Rakuten MLOps - Performance Monitoring"**

The dashboard includes:
- **Service Health Overview** — UP/DOWN status for all 4 application services
- **Request Rate** — requests per second per service/endpoint
- **Request Latency (p95)** — response time percentiles
- **Predictions by Class** — distribution of predicted categories
- **Model Inference Latency** — p50/p95/p99 inference time
- **Prediction Confidence** — confidence score distribution
- **Total Predictions** — counter of all predictions made
- **Training Status** — IDLE/TRAINING indicator
- **Training Loss & Accuracy** — latest training metrics

---

### 23. Stop everything

```bash
docker-compose down
```

---

## Full Pipeline Test (copy-paste sequence)

```bash
# 1. Start all 7 services
docker-compose up -d --build
sleep 40

# 2. Verify all services are healthy
curl http://localhost:8080/health

# 3. Load and prepare data
curl -X POST http://localhost:5001/data/load -H "Content-Type: application/json" -d '{}'
curl -X POST http://localhost:5001/data/split -H "Content-Type: application/json" -d '{"samples_per_class": 600}'
curl -X POST http://localhost:8080/api/v1/data/preprocess -H "Content-Type: application/json" -d '{}'

# 4. Train model
curl -X POST http://localhost:8080/api/v1/train -H "Content-Type: application/json" -d '{"epochs": 5, "batch_size": 32}'

# 5. Poll training status (repeat until progress = 100)
curl http://localhost:8080/api/v1/train/status

# 6. Load model and predict
curl -X POST http://localhost:5003/model/load -H "Content-Type: application/json" -d '{}'
curl -X POST http://localhost:8080/api/v1/predict -H "Content-Type: application/json" -d '{"text": "Samsung Galaxy S21 smartphone"}'

# 7. Verify monitoring stack
curl http://localhost:8080/metrics           # Prometheus metrics from Gateway
curl http://localhost:9090/api/v1/targets    # Prometheus scraping targets
curl http://localhost:3000/api/health        # Grafana health

# 8. Open dashboards in browser
#    - Grafana:    http://localhost:3000  (admin/admin)
#    - Prometheus: http://localhost:9090
#    - MLflow:     http://localhost:5000

# 9. Cleanup
docker-compose down
```
