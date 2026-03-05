import json
import os
from datetime import datetime

import mlflow
import mlflow.tensorflow
import tensorflow as tf
from tensorflow import keras

from features.build_features import DataImporter, TextPreprocessor
from models.train_model import TextLSTMModel, MLflowCallback


def train_with_mlflow():
    """Training function with MLflow tracking"""

    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow:5000"))

    experiment_name = f"rakuten_classification_{datetime.now().strftime('%Y%m%d')}"
    mlflow.set_experiment(experiment_name)

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

        mlflow.log_param("train_samples", len(X_train))
        mlflow.log_param("val_samples", len(X_val))

        # Preprocess text
        print("Preprocessing data...")
        text_preprocessor = TextPreprocessor()
        text_preprocessor.preprocess_text_in_df(X_train, columns=["description"])
        text_preprocessor.preprocess_text_in_df(X_val, columns=["description"])

        # Train LSTM model
        print("Training LSTM Model...")
        text_lstm_model = TextLSTMModel()
        history = text_lstm_model.preprocess_and_fit(
            X_train, y_train, X_val, y_val,
            mlflow_callback=MLflowCallback(model_name="lstm")
        )

        # Log final metrics and write metrics.json for DVC
        if history and hasattr(history, 'history'):
            final_loss = history.history.get('loss', [0])[-1]
            final_acc = history.history.get('accuracy', [0])[-1]
            val_loss = history.history.get('val_loss', [0])[-1]
            val_acc = history.history.get('val_accuracy', [0])[-1]

            mlflow.log_metric("final_train_loss", final_loss)
            mlflow.log_metric("final_train_accuracy", final_acc)
            mlflow.log_metric("final_val_loss", val_loss)
            mlflow.log_metric("final_val_accuracy", val_acc)

            # Write metrics file for DVC tracking
            metrics = {
                "val_accuracy": float(val_acc),
                "val_loss": float(val_loss),
                "train_accuracy": float(final_acc),
                "train_loss": float(final_loss)
            }
            with open("models/metrics.json", "w") as f:
                json.dump(metrics, f)

        # Log model and artifacts to MLflow
        print("Logging model to MLflow...")
        mlflow.tensorflow.log_model(
            text_lstm_model.model,
            "lstm_model",
            registered_model_name="rakuten_lstm_classifier"
        )
        mlflow.log_artifact("models/tokenizer_config.json")
        mlflow.log_artifact("models/mapper.pkl")
        mlflow.log_artifact("models/mapper.json")

        print(f"Training complete! Run ID: {run.info.run_id}")

        return run.info.run_id


if __name__ == "__main__":
    train_with_mlflow()