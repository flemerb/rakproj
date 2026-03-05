"""
Data Service - Handles data loading and preprocessing
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import sys

# Add src to path
sys.path.insert(0, '/app/src')

from features.build_features import DataImporter, TextPreprocessor, ImagePreprocessor

app = Flask(__name__)
CORS(app)

DATA_PATH = os.environ.get('DATA_PATH', '/app/data')
PREPROCESSED_PATH = os.environ.get('PREPROCESSED_PATH', '/app/data/preprocessed')


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
