"""
Prediction Service - Handles model inference
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import tokenizer_from_json
import numpy as np
import json
import os
import sys

# Add src to path
sys.path.insert(0, '/app/src')

from features.build_features import TextPreprocessor

app = Flask(__name__)
CORS(app)

MODELS_PATH = os.environ.get('MODELS_PATH', '/app/models')
MLFLOW_TRACKING_URI = os.environ.get('MLFLOW_TRACKING_URI', 'http://mlflow:5000')

# Global model and tokenizer
model = None
tokenizer = None
mapper = None
inverse_mapper = None


def load_model_and_artifacts():
    """Load model, tokenizer and mapper"""
    global model, tokenizer, mapper, inverse_mapper
    
    try:
        # Load model
        model_path = f"{MODELS_PATH}/best_lstm_model.h5"
        if os.path.exists(model_path):
            model = tf.keras.models.load_model(model_path)
            print(f"Model loaded from {model_path}")
        
        # Load tokenizer
        tokenizer_path = f"{MODELS_PATH}/tokenizer_config.json"
        if os.path.exists(tokenizer_path):
            with open(tokenizer_path, 'r', encoding='utf-8') as f:
                tokenizer_json = f.read()
                tokenizer = tokenizer_from_json(tokenizer_json)
            print(f"Tokenizer loaded from {tokenizer_path}")
        
        # Load mapper
        mapper_path = f"{MODELS_PATH}/mapper.json"
        if os.path.exists(mapper_path):
            with open(mapper_path, 'r', encoding='utf-8') as f:
                mapper_raw = json.load(f)
                mapper = {int(k): int(v) for k, v in mapper_raw.items()}
                inverse_mapper = {v: k for k, v in mapper.items()}
            print(f"Mapper loaded from {mapper_path}")
        
        return True
    except Exception as e:
        print(f"Error loading model: {e}")
        return False


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'prediction_service',
        'model_loaded': model is not None,
        'tokenizer_loaded': tokenizer is not None,
        'mapper_loaded': mapper is not None
    })


@app.route('/model/info', methods=['GET'])
def model_info():
    """Get model information"""
    return jsonify({
        'status': 'success',
        'model_loaded': model is not None,
        'model_path': MODELS_PATH,
        'num_classes': 27,
        'max_sequence_length': 10
    })


@app.route('/model/load', methods=['POST'])
def load_model_endpoint():
    """Load or reload model"""
    data = request.get_json() or {}
    model_version = data.get('version', 'latest')
    
    success = load_model_and_artifacts()
    
    if success:
        return jsonify({
            'status': 'success',
            'message': 'Model loaded successfully'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to load model'
        }), 500


@app.route('/predict', methods=['POST'])
def predict():
    """Make prediction on input text"""
    if model is None or tokenizer is None:
        return jsonify({
            'status': 'error',
            'message': 'Model not loaded'
        }), 500
    
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({
                'status': 'error',
                'message': 'No text provided'
            }), 400
        
        # Preprocess text
        preprocessor = TextPreprocessor()
        cleaned_text = preprocessor.preprocess_text(text)

        # Tokenize and pad
        sequences = tokenizer.texts_to_sequences([cleaned_text])
        padded = pad_sequences(sequences, maxlen=10, padding='post')
        
        # Predict
        predictions = model.predict(padded)
        predicted_class = int(np.argmax(predictions[0]))
        confidence = float(np.max(predictions[0]))
        
        # Get real category if mapper exists
        real_category = inverse_mapper.get(predicted_class, predicted_class) if inverse_mapper else predicted_class
        
        return jsonify({
            'status': 'success',
            'predicted_class': predicted_class,
            'real_category': real_category,
            'confidence': confidence,
            'all_probabilities': predictions[0].tolist()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """Make predictions on multiple texts"""
    if model is None or tokenizer is None:
        return jsonify({
            'status': 'error',
            'message': 'Model not loaded'
        }), 500
    
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        
        if not texts:
            return jsonify({
                'status': 'error',
                'message': 'No texts provided'
            }), 400
        
        results = []
        preprocessor = TextPreprocessor()
        
        for text in texts:
            cleaned_text = preprocessor.preprocess_text(text)
            sequences = tokenizer.texts_to_sequences([cleaned_text])
            padded = pad_sequences(sequences, maxlen=10, padding='post')
            
            predictions = model.predict(padded)
            predicted_class = int(np.argmax(predictions[0]))
            confidence = float(np.max(predictions[0]))
            
            results.append({
                'text': text[:50] + '...' if len(text) > 50 else text,
                'predicted_class': predicted_class,
                'confidence': confidence
            })
        
        return jsonify({
            'status': 'success',
            'predictions': results
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    # Try to load model on startup
    load_model_and_artifacts()
    app.run(host='0.0.0.0', port=5003, debug=True)
