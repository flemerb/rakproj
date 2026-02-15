from features.build_features import DataImporter, TextPreprocessor, ImagePreprocessor
from models.train_model import TextLSTMModel, ImageVGG16Model, concatenate, MLflowCallback
from tensorflow import keras
import pickle
import tensorflow as tf
import mlflow
import mlflow.tensorflow
import os
from datetime import datetime


def train_with_mlflow():
    """Training function with MLflow tracking"""
    
    # Set MLflow tracking URI (local or remote server)
    mlflow.set_tracking_uri("file:///home/anas/rakproj/mlruns")
    
    # Create or get experiment
    experiment_name = f"rakuten_classification_{datetime.now().strftime('%Y%m%d')}"
    mlflow.set_experiment(experiment_name)
    
    # Start MLflow run
    with mlflow.start_run(run_name="lstm_training") as run:
        
        # Log parameters
        mlflow.log_param("model_type", "LSTM")
        mlflow.log_param("max_words", 10000)
        mlflow.log_param("max_sequence_length", 10)
        mlflow.log_param("embedding_dim", 128)
        mlflow.log_param("lstm_units", 128)
        mlflow.log_param("num_classes", 27)
        
        # Data loading
        print("Loading data...")
        data_importer = DataImporter()
        df = data_importer.load_data()
        X_train, X_val, _, y_train, y_val, _ = data_importer.split_train_test(df)
        
        # Log data info
        mlflow.log_param("train_samples", len(X_train))
        mlflow.log_param("val_samples", len(X_val))
        
        # Preprocess text and images
        print("Preprocessing data...")
        text_preprocessor = TextPreprocessor()
        image_preprocessor = ImagePreprocessor()
        text_preprocessor.preprocess_text_in_df(X_train, columns=["description"])
        text_preprocessor.preprocess_text_in_df(X_val, columns=["description"])
        image_preprocessor.preprocess_images_in_df(X_train)
        image_preprocessor.preprocess_images_in_df(X_val)
        
        # Train LSTM model with MLflow callback
        print("Training LSTM Model...")
        text_lstm_model = TextLSTMModel()
        
        # Add MLflow callback to the training
        history = text_lstm_model.preprocess_and_fit(
            X_train, y_train, X_val, y_val,
            mlflow_callback=MLflowCallback(model_name="lstm")
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
        
        # Log model
        print("Logging model to MLflow...")
        mlflow.tensorflow.log_model(
            text_lstm_model.model,
            "lstm_model",
            registered_model_name="rakuten_lstm_classifier"
        )
        
        # Log artifacts (tokenizer, mapper)
        mlflow.log_artifact("models/tokenizer_config.json")
        mlflow.log_artifact("models/mapper.pkl")
        
        print(f"Training complete! Run ID: {run.info.run_id}")
        print(f"View at: mlflow ui --backend-store-uri file:///home/anas/rakproj/mlruns")
        
        return run.info.run_id


if __name__ == "__main__":
    train_with_mlflow()

