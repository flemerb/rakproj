"""
API Gateway - Routes requests to appropriate microservices
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)
CORS(app)

# Service URLs
DATA_SERVICE_URL = os.environ.get('DATA_SERVICE_URL', 'http://data_service:5001')
TRAINING_SERVICE_URL = os.environ.get('TRAINING_SERVICE_URL', 'http://training_service:5002')
PREDICTION_SERVICE_URL = os.environ.get('PREDICTION_SERVICE_URL', 'http://prediction_service:5003')
MLFLOW_URL = os.environ.get('MLFLOW_URL', 'http://mlflow:5000')

# Prometheus metrics
REQUEST_COUNT = Counter(
    'gateway_requests_total',
    'Total requests to API Gateway',
    ['method', 'endpoint', 'status']
)
REQUEST_LATENCY = Histogram(
    'gateway_request_duration_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)
SERVICES_UP = Gauge(
    'gateway_service_up',
    'Whether a downstream service is up (1) or down (0)',
    ['service']
)


@app.before_request
def start_timer():
    request._start_time = time.time()


@app.after_request
def record_metrics(response):
    latency = time.time() - getattr(request, '_start_time', time.time())
    endpoint = request.path
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=endpoint
    ).observe(latency)
    return response


@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API overview"""
    return jsonify({
        'service': 'API Gateway',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health (GET)',
            'predict': '/api/v1/predict (POST)',
            'train': '/api/v1/train (POST)',
            'data': '/api/v1/data (GET)',
            'services': '/api/v1/services (GET)',
            'metrics': '/metrics (GET) - Prometheus metrics'
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """Check health of all services"""
    services_health = {}

    # Check Data Service
    try:
        response = requests.get(f"{DATA_SERVICE_URL}/health", timeout=5)
        services_health['data_service'] = response.json()
        SERVICES_UP.labels(service='data_service').set(1)
    except:
        services_health['data_service'] = {'status': 'unhealthy'}
        SERVICES_UP.labels(service='data_service').set(0)

    # Check Training Service
    try:
        response = requests.get(f"{TRAINING_SERVICE_URL}/health", timeout=5)
        services_health['training_service'] = response.json()
        SERVICES_UP.labels(service='training_service').set(1)
    except:
        services_health['training_service'] = {'status': 'unhealthy'}
        SERVICES_UP.labels(service='training_service').set(0)

    # Check Prediction Service
    try:
        response = requests.get(f"{PREDICTION_SERVICE_URL}/health", timeout=5)
        services_health['prediction_service'] = response.json()
        SERVICES_UP.labels(service='prediction_service').set(1)
    except:
        services_health['prediction_service'] = {'status': 'unhealthy'}
        SERVICES_UP.labels(service='prediction_service').set(0)

    # Check MLflow
    try:
        response = requests.get(f"{MLFLOW_URL}/health", timeout=5)
        services_health['mlflow'] = {'status': 'healthy'}
        SERVICES_UP.labels(service='mlflow').set(1)
    except:
        services_health['mlflow'] = {'status': 'unhealthy'}
        SERVICES_UP.labels(service='mlflow').set(0)

    all_healthy = all(
        s.get('status') == 'healthy' or s.get('status') == 'running'
        for s in services_health.values()
    )

    return jsonify({
        'status': 'healthy' if all_healthy else 'degraded',
        'services': services_health
    })


@app.route('/api/v1/services', methods=['GET'])
def list_services():
    """List all available services"""
    return jsonify({
        'services': [
            {
                'name': 'data_service',
                'url': DATA_SERVICE_URL,
                'endpoints': ['/health', '/data/load', '/data/split', '/data/preprocess', '/data/status']
            },
            {
                'name': 'training_service',
                'url': TRAINING_SERVICE_URL,
                'endpoints': ['/health', '/train/start', '/train/status', '/train/metrics', '/models/list']
            },
            {
                'name': 'prediction_service',
                'url': PREDICTION_SERVICE_URL,
                'endpoints': ['/health', '/predict', '/predict/batch', '/model/info', '/model/load']
            },
            {
                'name': 'mlflow',
                'url': MLFLOW_URL,
                'description': 'MLflow tracking server'
            }
        ]
    })


@app.route('/api/v1/predict', methods=['POST'])
def predict():
    """Forward prediction request to prediction service"""
    try:
        response = requests.post(
            f"{PREDICTION_SERVICE_URL}/predict",
            json=request.get_json(),
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'Prediction service unavailable: {str(e)}'
        }), 503


@app.route('/api/v1/predict/batch', methods=['POST'])
def predict_batch():
    """Forward batch prediction request"""
    try:
        response = requests.post(
            f"{PREDICTION_SERVICE_URL}/predict/batch",
            json=request.get_json(),
            timeout=60
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'Prediction service unavailable: {str(e)}'
        }), 503


@app.route('/api/v1/train', methods=['POST'])
def train():
    """Forward training request to training service"""
    try:
        response = requests.post(
            f"{TRAINING_SERVICE_URL}/train/start",
            json=request.get_json(),
            timeout=10
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'Training service unavailable: {str(e)}'
        }), 503


@app.route('/api/v1/train/status', methods=['GET'])
def train_status():
    """Get training status"""
    try:
        response = requests.get(
            f"{TRAINING_SERVICE_URL}/train/status",
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'Training service unavailable: {str(e)}'
        }), 503


@app.route('/api/v1/data', methods=['GET'])
def data_status():
    """Get data status"""
    try:
        response = requests.get(
            f"{DATA_SERVICE_URL}/data/status",
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'Data service unavailable: {str(e)}'
        }), 503


@app.route('/api/v1/data/preprocess', methods=['POST'])
def preprocess_data():
    """Forward preprocessing request"""
    try:
        response = requests.post(
            f"{DATA_SERVICE_URL}/data/preprocess",
            json=request.get_json(),
            timeout=60
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'Data service unavailable: {str(e)}'
        }), 503


@app.route('/api/v1/models', methods=['GET'])
def list_models():
    """List registered models"""
    try:
        response = requests.get(
            f"{TRAINING_SERVICE_URL}/models/list",
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'Training service unavailable: {str(e)}'
        }), 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
