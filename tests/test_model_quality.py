"""
tests/test_model_quality.py

Model quality gate — runs after training, before deployment.
Loads the trained model and asserts it meets minimum accuracy
thresholds on a held-out test set.

Run in CI immediately after the training step:

    pytest tests/test_model_quality.py --tb=short

Required files (produced by the training pipeline):
    models/best_lstm_model.h5
    models/tokenizer_config.json
    models/mapper.json
    data/preprocessed/X_train_update.csv
    data/preprocessed/Y_train_CVw08PX.csv

Environment variables:
    MODELS_PATH          Path to models dir (default: models)
    PREPROCESSED_PATH    Path to preprocessed data (default: data/preprocessed)
    MIN_ACCURACY         Minimum acceptable accuracy (default: 0.75)
    MIN_VAL_ACCURACY     Minimum acceptable val accuracy (default: 0.70)
"""

import os
import sys
import json
import pytest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

MODELS_PATH       = os.environ.get("MODELS_PATH", "models")
PREPROCESSED_PATH = os.environ.get("PREPROCESSED_PATH", "data/preprocessed")
MIN_ACCURACY      = float(os.environ.get("MIN_ACCURACY", "0.75"))
MIN_VAL_ACCURACY  = float(os.environ.get("MIN_VAL_ACCURACY", "0.70"))

MODEL_PATH     = os.path.join(MODELS_PATH, "best_lstm_model.h5")
TOKENIZER_PATH = os.path.join(MODELS_PATH, "tokenizer_config.json")
MAPPER_PATH    = os.path.join(MODELS_PATH, "mapper.json")


# ---------------------------------------------------------------------------
# Skip entire module if model files don't exist
# (so unit tests still pass in environments without trained artifacts)
# ---------------------------------------------------------------------------

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "quality_gate: marks tests as model quality gate (require trained model)"
    )


def _model_files_present():
    return all(os.path.exists(p) for p in [MODEL_PATH, TOKENIZER_PATH, MAPPER_PATH])


def _data_files_present():
    return (
        os.path.exists(os.path.join(PREPROCESSED_PATH, "X_train_update.csv")) and
        os.path.exists(os.path.join(PREPROCESSED_PATH, "Y_train_CVw08PX.csv"))
    )


requires_model = pytest.mark.skipif(
    not _model_files_present(),
    reason="Trained model artifacts not found — run training first"
)
requires_data = pytest.mark.skipif(
    not _data_files_present(),
    reason="Preprocessed data not found"
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def model():
    import tensorflow as tf
    return tf.keras.models.load_model(MODEL_PATH)


@pytest.fixture(scope="module")
def tokenizer():
    from tensorflow.keras.preprocessing.text import tokenizer_from_json
    with open(TOKENIZER_PATH, "r", encoding="utf-8") as f:
        return tokenizer_from_json(f.read())


@pytest.fixture(scope="module")
def mapper():
    with open(MAPPER_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return {int(k): int(v) for k, v in raw.items()}


@pytest.fixture(scope="module")
def test_data(mapper):
    """Load and prepare the held-out test split."""
    import pandas as pd
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    from features.build_features import DataImporter, TextPreprocessor

    importer = DataImporter(filepath=PREPROCESSED_PATH)
    df = importer.load_data()
    _, _, X_test, _, _, y_test = importer.split_train_test(df)

    preprocessor = TextPreprocessor()
    preprocessor.preprocess_text_in_df(X_test, columns=["description"])

    return X_test, y_test


# ---------------------------------------------------------------------------
# Artifact integrity checks
# ---------------------------------------------------------------------------

@pytest.mark.quality_gate
class TestModelArtifacts:

    @requires_model
    def test_model_file_exists(self):
        assert os.path.exists(MODEL_PATH), f"Model not found at {MODEL_PATH}"

    @requires_model
    def test_tokenizer_file_exists(self):
        assert os.path.exists(TOKENIZER_PATH)

    @requires_model
    def test_mapper_file_exists(self):
        assert os.path.exists(MAPPER_PATH)

    @requires_model
    def test_mapper_has_27_classes(self, mapper):
        assert len(mapper) == 27, \
            f"Expected 27 classes in mapper, got {len(mapper)}"

    @requires_model
    def test_mapper_indices_are_contiguous(self, mapper):
        """Indices must be 0..26 with no gaps."""
        assert set(mapper.keys()) == set(range(27)), \
            f"Mapper keys are not contiguous 0-26: {sorted(mapper.keys())}"

    @requires_model
    def test_model_loads_without_error(self, model):
        assert model is not None

    @requires_model
    def test_model_output_shape_is_27(self, model):
        assert model.output_shape[-1] == 27, \
            f"Model output should have 27 classes, got {model.output_shape[-1]}"

    @requires_model
    def test_model_input_sequence_length_is_10(self, model):
        assert model.input_shape[-1] == 10, \
            f"Model input length should be 10, got {model.input_shape[-1]}"


# ---------------------------------------------------------------------------
# Inference sanity checks
# ---------------------------------------------------------------------------

@pytest.mark.quality_gate
class TestModelInference:

    @requires_model
    def test_model_produces_probabilities_summing_to_1(self, model, tokenizer):
        from tensorflow.keras.preprocessing.sequence import pad_sequences

        sequences = tokenizer.texts_to_sequences(["chaise bureau bois"])
        padded = pad_sequences(sequences, maxlen=10, padding="post")
        preds = model.predict(padded, verbose=0)

        assert abs(preds[0].sum() - 1.0) < 1e-4, \
            f"Probabilities do not sum to 1: {preds[0].sum()}"

    @requires_model
    def test_model_confidence_is_between_0_and_1(self, model, tokenizer):
        from tensorflow.keras.preprocessing.sequence import pad_sequences

        sequences = tokenizer.texts_to_sequences(["livre roman policier"])
        padded = pad_sequences(sequences, maxlen=10, padding="post")
        preds = model.predict(padded, verbose=0)

        confidence = float(np.max(preds[0]))
        assert 0.0 <= confidence <= 1.0

    @requires_model
    def test_model_predicted_class_is_valid_index(self, model, tokenizer, mapper):
        from tensorflow.keras.preprocessing.sequence import pad_sequences

        sequences = tokenizer.texts_to_sequences(["téléphone samsung galaxy"])
        padded = pad_sequences(sequences, maxlen=10, padding="post")
        preds = model.predict(padded, verbose=0)

        predicted_index = int(np.argmax(preds[0]))
        assert predicted_index in mapper, \
            f"Predicted index {predicted_index} not in mapper"

    @requires_model
    def test_model_handles_empty_text_without_crash(self, model, tokenizer):
        from tensorflow.keras.preprocessing.sequence import pad_sequences

        sequences = tokenizer.texts_to_sequences([""])
        padded = pad_sequences(sequences, maxlen=10, padding="post")
        preds = model.predict(padded, verbose=0)
        assert preds.shape == (1, 27)

    @requires_model
    def test_model_handles_unknown_words(self, model, tokenizer):
        from tensorflow.keras.preprocessing.sequence import pad_sequences

        sequences = tokenizer.texts_to_sequences(["xyzzy qqqq zzzz"])
        padded = pad_sequences(sequences, maxlen=10, padding="post")
        preds = model.predict(padded, verbose=0)
        assert preds.shape == (1, 27)


# ---------------------------------------------------------------------------
# Accuracy thresholds — the actual quality gate
# ---------------------------------------------------------------------------

@pytest.mark.quality_gate
class TestModelAccuracy:

    @requires_model
    @requires_data
    def test_test_set_accuracy_above_threshold(self, model, tokenizer, test_data):
        """
        Core quality gate: model must achieve at least MIN_ACCURACY on the
        held-out test set. If this fails, the model must NOT be deployed.
        """
        from tensorflow.keras.preprocessing.sequence import pad_sequences

        X_test, y_test = test_data
        sequences = tokenizer.texts_to_sequences(X_test["description"].tolist())
        padded = pad_sequences(sequences, maxlen=10, padding="post")

        preds = model.predict(padded, verbose=0)
        predicted_classes = np.argmax(preds, axis=1)

        correct = (predicted_classes == y_test.values).sum()
        accuracy = correct / len(y_test)

        print(f"\nTest set accuracy: {accuracy:.4f} (threshold: {MIN_ACCURACY})")

        assert accuracy >= MIN_ACCURACY, (
            f"Model accuracy {accuracy:.4f} is below minimum threshold {MIN_ACCURACY}. "
            f"Do NOT deploy this model."
        )

    @requires_model
    @requires_data
    def test_no_class_has_zero_predictions(self, model, tokenizer, test_data):
        """
        A degenerate model might learn to always predict one class.
        Every class should appear in the predictions at least once.
        """
        from tensorflow.keras.preprocessing.sequence import pad_sequences

        X_test, y_test = test_data
        sequences = tokenizer.texts_to_sequences(X_test["description"].tolist())
        padded = pad_sequences(sequences, maxlen=10, padding="post")

        preds = model.predict(padded, verbose=0)
        predicted_classes = np.argmax(preds, axis=1)
        unique_predictions = set(predicted_classes.tolist())

        assert len(unique_predictions) == 27, (
            f"Model only predicts {len(unique_predictions)} distinct classes out of 27. "
            f"Possible mode collapse."
        )

    @requires_model
    @requires_data
    def test_per_class_accuracy_all_above_minimum(self, model, tokenizer, test_data, mapper):
        """
        No single class should be catastrophically bad.
        Each class must achieve at least 40% accuracy individually.
        """
        from tensorflow.keras.preprocessing.sequence import pad_sequences
        import pandas as pd

        X_test, y_test = test_data
        sequences = tokenizer.texts_to_sequences(X_test["description"].tolist())
        padded = pad_sequences(sequences, maxlen=10, padding="post")

        preds = model.predict(padded, verbose=0)
        predicted_classes = np.argmax(preds, axis=1)

        PER_CLASS_MIN = 0.40
        failures = []

        for cls_idx in range(27):
            mask = y_test.values == cls_idx
            if mask.sum() == 0:
                continue
            cls_acc = (predicted_classes[mask] == cls_idx).sum() / mask.sum()
            if cls_acc < PER_CLASS_MIN:
                category_code = mapper.get(cls_idx, cls_idx)
                failures.append(
                    f"  Class index {cls_idx} (category {category_code}): "
                    f"accuracy {cls_acc:.4f} < {PER_CLASS_MIN}"
                )

        assert not failures, (
            f"The following classes are below per-class minimum ({PER_CLASS_MIN}):\n"
            + "\n".join(failures)
        )

    @requires_model
    @requires_data
    def test_model_accuracy_better_than_random(self, model, tokenizer, test_data):
        """Sanity check: model must beat random chance (1/27 ≈ 0.037)."""
        from tensorflow.keras.preprocessing.sequence import pad_sequences

        X_test, y_test = test_data
        sequences = tokenizer.texts_to_sequences(X_test["description"].tolist())
        padded = pad_sequences(sequences, maxlen=10, padding="post")

        preds = model.predict(padded, verbose=0)
        predicted_classes = np.argmax(preds, axis=1)

        accuracy = (predicted_classes == y_test.values).sum() / len(y_test)
        random_baseline = 1 / 27

        assert accuracy > random_baseline * 3, (
            f"Model accuracy {accuracy:.4f} is barely above random ({random_baseline:.4f}). "
            f"Something is wrong with training."
        )
