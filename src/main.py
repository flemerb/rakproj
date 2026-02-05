from features.build_features import DataImporter, TextPreprocessor, ImagePreprocessor
from models.train_model import TextLSTMModel, ImageVGG16Model, concatenate
from tensorflow import keras
import pickle
import tensorflow as tf


data_importer = DataImporter()
df = data_importer.load_data()
X_train, X_val, _, y_train, y_val, _ = data_importer.split_train_test(df)

# Preprocess text and images
text_preprocessor = TextPreprocessor()
image_preprocessor = ImagePreprocessor()
text_preprocessor.preprocess_text_in_df(X_train, columns=["description"])
text_preprocessor.preprocess_text_in_df(X_val, columns=["description"])
image_preprocessor.preprocess_images_in_df(X_train)
image_preprocessor.preprocess_images_in_df(X_val)

# Train LSTM model
print("Training LSTM Model")
text_lstm_model = TextLSTMModel()
text_lstm_model.preprocess_and_fit(X_train, y_train, X_val, y_val)
print("Finished training LSTM")

