"""
Training Service - Handles model training with MLflow tracking
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import mlflow
import mlflow.tensorflow
import os
import sys
import yaml
import threading

# Add src to path
sys.path.insert(0, '/app/src')

from features.build_features import DataImporter, TextPreprocessor, ImagePreprocessor
from models.train_model import TextLSTMModel, MLflowCallback

app = Flask(__name__)
CORS(app)

MLFLOW_TRACKING_URI = os.environ.get('MLFLOW_TRACKING_URI', 'http://mlflow:5000')
PREPROCESSED_PATH = os.environ.get('PREPROCESSED_PATH', '/app/data/preprocessed')
MODELS_PATH = os.environ.get('MODELS_PATH', '/app/models')

# Training status
training_status = {
    'is_training': False,
    'progress': 0,
    'current_epoch': 0,
    'metrics': {}
}


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'training_service',
        'mlflow_connected': check_mlflow_connection()
    })


def check_mlflow_connection():
    """Check if MLflow server is accessible"""
    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        return True
    except:
        return False


@app.route('/train/start', methods=['POST'])
def start_training():
    """Start model training"""
    global training_status
    
    if training_status['is_training']:
        return jsonify({
            'status': 'error',
            'message': 'Training already in progress'
        }), 400
    
    try:
        data = request.get_json() or {}
        epochs = data.get('epochs', 10)
        batch_size = data.get('batch_size', 32)
        
        # Start training in background thread
        thread = threading.Thread(
            target=train_model,
            args=(epochs, batch_size)
        )
        thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'Training started'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


def train_model(epochs, batch_size):
    """Train the LSTM model with MLflow tracking"""
    global training_status
    
    training_status['is_training'] = True
    training_status['progress'] = 0
    training_status['metrics'] = {}
    
    try:
        # Set MLflow tracking URI
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        mlflow.set_experiment("rakuten_classification")
        
        with mlflow.start_run(run_name="lstm_training") as run:
            # Log parameters
            mlflow.log_param("model_type", "LSTM")
            mlflow.log_param("epochs", epochs)
            mlflow.log_param("batch_size", batch_size)
            
            # Load and preprocess data
            data_importer = DataImporter(filepath=PREPROCESSED_PATH)
            df = data_importer.load_data()
            X_train, X_val, _, y_train, y_val, _ = data_importer.split_train_test(df)
            
            mlflow.log_param("train_samples", len(X_train))
            mlflow.log_param("val_samples", len(X_val))
            
            # Preprocess
            text_preprocessor = TextPreprocessor()
            text_preprocessor.preprocess_text_in_df(X_train, columns=["description"])
            text_preprocessor.preprocess_text_in_df(X_val, columns=["description"])
            
            # Train model
            model = TextLSTMModel()
            history = model.preprocess_and_fit(
                X_train, y_train, X_val, y_val,
                mlflow_callback=MLflowCallback(model_name="lstm"),
                epochs=epochs,
                batch_size=batch_size
            )
            
            # Log final metrics
            if history and hasattr(history, 'history'):
                final_loss = history.history.get('loss', [0])[-1]
                final_acc = history.history.get('accuracy', [0])[-1]
                val_loss = history.history.get('val_loss', [0])[-1]
                val_acc = history.history.get('val_accuracy', [0])[-1]
                
                mlflow.log_metric("final_train_loss", final_loss)
                mlflow.log_metric("final_train_accuracy", final_acc)
                mlflow.log_metric("final_val_loss", val_loss)
                mlflow.log_metric("final_val_accuracy", val_acc)
                
                training_status['metrics'] = {
                    'train_loss': final_loss,
                    'train_accuracy': final_acc,
                    'val_loss': val_loss,
                    'val_accuracy': val_acc
                }
            
            # Log model
            mlflow.tensorflow.log_model(
                model.model,
                "lstm_model",
                registered_model_name="rakuten_lstm_classifier"
            )
            
            # Log artifacts
            mlflow.log_artifact(f"{MODELS_PATH}/tokenizer_config.json")
            mlflow.log_artifact(f"{MODELS_PATH}/mapper.pkl")
            
            training_status['progress'] = 100
            
    except Exception as e:
        training_status['metrics']['error'] = str(e)
    finally:
        training_status['is_training'] = False


@app.route('/train/status', methods=['GET'])
def get_training_status():
    """Get current training status"""
    return jsonify({
        'status': 'success',
        'training_status': training_status
    })


@app.route('/train/metrics', methods=['GET'])
def get_metrics():
    """Get training metrics"""
    return jsonify({
        'status': 'success',
        'metrics': training_status['metrics']
    })


@app.route('/models/list', methods=['GET'])
def list_models():
    """List registered models from MLflow"""
    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        client = mlflow.tracking.MlflowClient()
        
        registered_models = client.search_registered_models()
        models = []
        for rm in registered_models:
            models.append({
                'name': rm.name,
                'latest_versions': [v.version for v in client.search_model_versions(f"name='{rm.name}'")]
            })
        
        return jsonify({
            'status': 'success',
            'models': models
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
