# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import tokenizer_from_json
import json
import pickle
import os

app = Flask(__name__)
CORS(app)

# Load model and preprocessing objects
MODEL_PATH = 'models/best_lstm_model.h5'
TOKENIZER_PATH = 'models/tokenizer_config.json'
MAPPER_PATH = 'models/mapper.json'

# Global variables for model and tokenizer
model = None
tokenizer = None
mapper = None
inverse_mapper = None


def load_model_and_tokenizer():
    """Load model, tokenizer, and mapper on startup"""
    global model, tokenizer, mapper, inverse_mapper
    
    try:
        # Load model
        if os.path.exists(MODEL_PATH):
            model = tf.keras.models.load_model(MODEL_PATH)
            print(f"odel loaded from {MODEL_PATH}")
        else:
            print(f"Model not found at {MODEL_PATH}")
            return False
        
        # Load tokenizer
        if os.path.exists(TOKENIZER_PATH):
            with open(TOKENIZER_PATH, 'r', encoding='utf-8') as f:
                tokenizer_json = f.read()
                tokenizer = tokenizer_from_json(tokenizer_json)
            print(f"Tokenizer loaded from {TOKENIZER_PATH}")
        else:
            print(f"Tokenizer not found at {TOKENIZER_PATH}")
            return False
        
        # Load mapper and convert to integers
        if os.path.exists(MAPPER_PATH):
            with open(MAPPER_PATH, 'r', encoding='utf-8') as f:
                mapper_raw = json.load(f)
                # Convert strings to integers: {0: 10, 1: 2280, ...}
                mapper = {int(k): int(v) for k, v in mapper_raw.items()}
                # Create inverse mapper: {10: 0, 2280: 1, ...}
                inverse_mapper = {v: k for k, v in mapper.items()}
            print(f"Mapper loaded from {MAPPER_PATH}")
            print(f"Example: index 0 → category {mapper[0]}")
        else:
            print(f"Mapper not found at {MAPPER_PATH}")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ Error loading model/tokenizer: {e}")
        import traceback
        traceback.print_exc()
        return False


@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'message': 'Rakuten Product Classification API',
        'model_loaded': model is not None,
        'endpoints': {
            'health': '/',
            'predict': '/predict (POST)',
            'info': '/info (GET)'
        }
    })


@app.route('/info', methods=['GET'])
def info():
    """Get API information"""
    return jsonify({
        'model_path': MODEL_PATH,
        'model_loaded': model is not None,
        'tokenizer_loaded': tokenizer is not None,
        'mapper_loaded': mapper is not None,
        'num_classes': 27,
        'max_sequence_length': 10
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict product category from description
    
    Request body:
    {
        "description": "Product description text"
    }
    
    Response:
    {
        "predicted_category": 10,
        "confidence": 0.85,
        "top_5_predictions": {...}
    }
    """
    try:
        # Check if model is loaded
        if model is None or tokenizer is None or mapper is None:
            return jsonify({
                'error': 'Model not loaded. Please restart the server.'
            }), 500
        
        # Get request data
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({
                'error': 'Missing "description" field in request body'
            }), 400
        
        description = data['description']
        
        if not description or not isinstance(description, str):
            return jsonify({
                'error': 'Description must be a non-empty string'
            }), 400
        
        # Preprocess text
        sequence = tokenizer.texts_to_sequences([description])
        padded_sequence = pad_sequences(sequence, maxlen=10, padding='post', truncating='post')
        
        # Make prediction
        predictions = model.predict(padded_sequence, verbose=0)
        predicted_index = int(predictions[0].argmax())
        confidence = float(predictions[0][predicted_index])
        
        # Convert index to prdtypecode using mapper
        predicted_category = int(mapper[predicted_index])
        
        # Get all probabilities mapped to categories
        all_probs = {
            int(mapper[i]): float(predictions[0][i]) 
            for i in range(len(predictions[0]))
        }
        
        # Sort by probability and get top 5
        sorted_probs = dict(sorted(all_probs.items(), key=lambda x: x[1], reverse=True)[:5])
        
        return jsonify({
            'predicted_category': predicted_category,
            'predicted_index': predicted_index,
            'confidence': confidence,
            'top_5_predictions': sorted_probs,
            'description': description
        })
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in prediction:")
        print(error_details)
        return jsonify({
            'error': f'Prediction failed: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("Starting Rakuten Product Classification API...")
    
    # Load model on startup
    if load_model_and_tokenizer():
        print("All components loaded successfully!")
        print("API is ready at http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("Failed to load required components. Exiting.")