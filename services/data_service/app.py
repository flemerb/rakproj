"""
Data Service - Handles data loading and preprocessing
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import sys
import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Add src to path
sys.path.insert(0, '/app/src')

from features.build_features import DataImporter, TextPreprocessor

app = Flask(__name__)
CORS(app)

DATA_PATH = os.environ.get('DATA_PATH', '/app/data')
PREPROCESSED_PATH = os.environ.get('PREPROCESSED_PATH', '/app/data/preprocessed')

# Prometheus metrics
REQUEST_COUNT = Counter(
    'data_service_requests_total',
    'Total requests to Data Service',
    ['method', 'endpoint', 'status']
)
REQUEST_LATENCY = Histogram(
    'data_service_request_duration_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)
DATA_RECORDS = Gauge(
    'data_service_records_loaded',
    'Number of data records loaded',
    ['split']
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


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'data_service'
    })


@app.route('/data/load', methods=['POST'])
def load_data():
    """Load raw data from CSV files"""
    try:
        data_importer = DataImporter(filepath=PREPROCESSED_PATH)
        df = data_importer.load_data()

        DATA_RECORDS.labels(split='total').set(len(df))

        return jsonify({
            'status': 'success',
            'message': 'Data loaded successfully',
            'shape': df.shape,
            'columns': list(df.columns)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/data/split', methods=['POST'])
def split_data():
    """Split data into train/validation/test sets"""
    try:
        data = request.get_json()
        samples_per_class = data.get('samples_per_class', 600)

        data_importer = DataImporter(filepath=PREPROCESSED_PATH)
        df = data_importer.load_data()
        X_train, X_val, X_test, y_train, y_val, y_test = data_importer.split_train_test(
            df, samples_per_class=samples_per_class
        )

        DATA_RECORDS.labels(split='train').set(len(X_train))
        DATA_RECORDS.labels(split='validation').set(len(X_val))
        DATA_RECORDS.labels(split='test').set(len(X_test))

        return jsonify({
            'status': 'success',
            'train_size': len(X_train),
            'val_size': len(X_val),
            'test_size': len(X_test)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/data/preprocess', methods=['POST'])
def preprocess_data():
    """Preprocess text and images"""
    try:
        data = request.get_json()
        text_columns = data.get('text_columns', ['description'])

        data_importer = DataImporter(filepath=PREPROCESSED_PATH)
        df = data_importer.load_data()
        X_train, X_val, X_test, y_train, y_val, y_test = data_importer.split_train_test(df)

        # Preprocess text
        text_preprocessor = TextPreprocessor()
        text_preprocessor.preprocess_text_in_df(X_train, columns=text_columns)
        text_preprocessor.preprocess_text_in_df(X_val, columns=text_columns)

        # Preprocess images
        image_preprocessor = ImagePreprocessor(filepath=f"{PREPROCESSED_PATH}/image_train")
        image_preprocessor.preprocess_images_in_df(X_train)
        image_preprocessor.preprocess_images_in_df(X_val)

        return jsonify({
            'status': 'success',
            'message': 'Data preprocessed successfully',
            'train_size': len(X_train),
            'val_size': len(X_val)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/data/status', methods=['GET'])
def data_status():
    """Check data status"""
    try:
        raw_exists = os.path.exists(f"{DATA_PATH}/raw")
        preprocessed_exists = os.path.exists(PREPROCESSED_PATH)

        files = []
        if preprocessed_exists:
            files = os.listdir(PREPROCESSED_PATH)

        return jsonify({
            'status': 'success',
            'raw_data_exists': raw_exists,
            'preprocessed_data_exists': preprocessed_exists,
            'files': files
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
