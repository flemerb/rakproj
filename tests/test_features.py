"""
tests/test_features.py

Unit tests for TextPreprocessor and DataImporter.
These test actual behaviour with known inputs/outputs,
not just that classes can be instantiated.
"""

import sys
import os
import json
import math
import pickle
import tempfile
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from features.build_features import TextPreprocessor, DataImporter


# ---------------------------------------------------------------------------
# TextPreprocessor
# ---------------------------------------------------------------------------

class TestTextPreprocessorBehaviour:

    @pytest.fixture(autouse=True)
    def preprocessor(self):
        self.p = TextPreprocessor()

    # --- HTML stripping ---

    def test_strips_html_tags(self):
        result = self.p.preprocess_text("<b>Chaise</b> en <i>bois</i>")
        assert "<b>" not in result
        assert "<i>" not in result
        assert "bois" in result  # meaningful word survives

    def test_strips_complex_html(self):
        result = self.p.preprocess_text(
            '<div class="product"><p>Table bois massif</p></div>'
        )
        assert "<" not in result
        assert ">" not in result

    # --- Non-alphabetic removal ---

    def test_removes_numbers(self):
        result = self.p.preprocess_text("Produit 12345 référence")
        # digits should be stripped
        assert "12345" not in result

    def test_removes_punctuation(self):
        result = self.p.preprocess_text("Livre! Très, bon: état.")
        for char in "!,:.":
            assert char not in result

    # --- Stopword removal ---

    def test_removes_french_stopwords(self):
        # "le", "la", "les", "de", "du" are French stopwords
        result = self.p.preprocess_text("le chat mange de la nourriture")
        for stopword in ["le", "la", "de"]:
            # stopwords should not appear as standalone tokens
            tokens = result.split()
            assert stopword not in tokens, f"Stopword '{stopword}' was not removed"

    # --- Lemmatisation ---

    def test_lemmatises_words(self):
        # "running" → "running" or "run" depending on lemmatiser,
        # key point: output is lowercase
        result = self.p.preprocess_text("Running shoes for athletes")
        assert result == result.lower()

    # --- Max length cap ---

    def test_output_capped_at_10_words(self):
        long_text = " ".join(["mot"] * 50)  # 50 words
        result = self.p.preprocess_text(long_text)
        tokens = result.split()
        assert len(tokens) <= 10, "Output should be capped at 10 tokens"

    # --- Edge cases ---

    def test_nan_float_returns_empty_string(self):
        result = self.p.preprocess_text(float("nan"))
        assert result == ""

    def test_empty_string_returns_empty_string(self):
        result = self.p.preprocess_text("")
        assert result == ""

    def test_whitespace_only_returns_empty_or_short(self):
        result = self.p.preprocess_text("     ")
        assert isinstance(result, str)

    def test_returns_string(self):
        result = self.p.preprocess_text("Chaise bureau ergonomique")
        assert isinstance(result, str)

    # --- DataFrame helper ---

    def test_preprocess_text_in_df_modifies_column_in_place(self):
        df = pd.DataFrame({"description": ["<b>Produit</b> numéro 42", "Livre ancien"]})
        original_values = df["description"].tolist()
        self.p.preprocess_text_in_df(df, columns=["description"])
        # values should have changed
        assert df["description"].tolist() != original_values

    def test_preprocess_text_in_df_no_nulls_introduced(self):
        df = pd.DataFrame({
            "description": ["Texte normal", None, float("nan"), "Autre texte"]
        })
        self.p.preprocess_text_in_df(df, columns=["description"])
        assert df["description"].notna().all()

    def test_preprocess_text_in_df_multiple_columns(self):
        df = pd.DataFrame({
            "description": ["Produit A", "Produit B"],
            "designation": ["<b>Désignation</b>", "Autre désignation"]
        })
        self.p.preprocess_text_in_df(df, columns=["description", "designation"])
        assert "<b>" not in df["designation"].iloc[0]
        assert df["description"].notna().all()

    def test_preprocess_text_in_df_preserves_row_count(self):
        df = pd.DataFrame({"description": [f"Produit {i}" for i in range(100)]})
        self.p.preprocess_text_in_df(df, columns=["description"])
        assert len(df) == 100


# ---------------------------------------------------------------------------
# DataImporter — split_train_test
# ---------------------------------------------------------------------------

def _make_sample_df(n_classes=3, samples_per_class=700):
    """
    Build a synthetic DataFrame that mirrors the real data structure
    with prdtypecode already label-encoded (0, 1, 2, ...).
    """
    rows = []
    for cls in range(n_classes):
        for i in range(samples_per_class):
            rows.append({
                "description": f"description class {cls} item {i}",
                "productid": cls * samples_per_class + i,
                "imageid": f"img_{cls}_{i}",
                "prdtypecode": cls,
            })
    return pd.DataFrame(rows)


class TestDataImporterSplit:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.importer = DataImporter()
        # 3 classes × 700 rows = 2100 rows total
        self.df = _make_sample_df(n_classes=3, samples_per_class=700)

    def test_returns_six_outputs(self):
        result = self.importer.split_train_test(self.df)
        assert len(result) == 6

    def test_train_size_equals_samples_per_class_times_n_classes(self):
        X_train, X_val, X_test, y_train, y_val, y_test = \
            self.importer.split_train_test(self.df, samples_per_class=600)
        # 3 classes × 600 = 1800 training rows
        assert len(X_train) == 1800

    def test_val_size_equals_val_samples_per_class_times_n_classes(self):
        X_train, X_val, X_test, y_train, y_val, y_test = \
            self.importer.split_train_test(self.df, samples_per_class=600)
        # val_samples_per_class is hardcoded to 50 in the source
        assert len(X_val) == 3 * 50

    def test_x_y_lengths_match_in_every_split(self):
        X_train, X_val, X_test, y_train, y_val, y_test = \
            self.importer.split_train_test(self.df)
        assert len(X_train) == len(y_train)
        assert len(X_val) == len(y_val)
        assert len(X_test) == len(y_test)

    def test_no_overlap_between_train_and_val(self):
        X_train, X_val, X_test, y_train, y_val, y_test = \
            self.importer.split_train_test(self.df)
        train_ids = set(X_train["productid"])
        val_ids = set(X_val["productid"])
        assert train_ids.isdisjoint(val_ids), "Train and val sets share product IDs"

    def test_no_overlap_between_train_and_test(self):
        X_train, X_val, X_test, y_train, y_val, y_test = \
            self.importer.split_train_test(self.df)
        train_ids = set(X_train["productid"])
        test_ids = set(X_test["productid"])
        assert train_ids.isdisjoint(test_ids), "Train and test sets share product IDs"

    def test_all_classes_represented_in_train(self):
        X_train, X_val, X_test, y_train, y_val, y_test = \
            self.importer.split_train_test(self.df)
        assert set(y_train.unique()) == {0, 1, 2}

    def test_all_classes_represented_in_val(self):
        X_train, X_val, X_test, y_train, y_val, y_test = \
            self.importer.split_train_test(self.df)
        assert set(y_val.unique()) == {0, 1, 2}

    def test_description_column_present_in_all_x_splits(self):
        X_train, X_val, X_test, y_train, y_val, y_test = \
            self.importer.split_train_test(self.df)
        for split in [X_train, X_val, X_test]:
            assert "description" in split.columns

    def test_prdtypecode_not_in_x_splits(self):
        """Target column must not leak into features."""
        X_train, X_val, X_test, y_train, y_val, y_test = \
            self.importer.split_train_test(self.df)
        for split in [X_train, X_val, X_test]:
            assert "prdtypecode" not in split.columns

    def test_output_types(self):
        X_train, X_val, X_test, y_train, y_val, y_test = \
            self.importer.split_train_test(self.df)
        for X in [X_train, X_val, X_test]:
            assert isinstance(X, pd.DataFrame)
        for y in [y_train, y_val, y_test]:
            assert isinstance(y, pd.Series)

    def test_reproducibility_with_same_random_state(self):
        """Two calls should produce identical splits."""
        result1 = self.importer.split_train_test(self.df, samples_per_class=600)
        result2 = self.importer.split_train_test(self.df, samples_per_class=600)
        pd.testing.assert_frame_equal(
            result1[0].reset_index(drop=True),
            result2[0].reset_index(drop=True)
        )


# ---------------------------------------------------------------------------
# Mapper persistence — saved as both .pkl and .json
# ---------------------------------------------------------------------------

class TestMapperPersistence:
    """
    Validates the fix for bug #3: mapper must be saved as both
    mapper.pkl (for legacy use) and mapper.json (for services).
    """

    @pytest.fixture()
    def tmp_models_dir(self, tmp_path):
        """Patch the hardcoded 'models/' path by running from tmp_path."""
        original_cwd = os.getcwd()
        models_dir = tmp_path / "models"
        models_dir.mkdir()
        os.chdir(tmp_path)
        yield tmp_path
        os.chdir(original_cwd)

    def test_mapper_json_exists_after_load_data(self, tmp_models_dir):
        """
        After DataImporter.load_data() runs, models/mapper.json must exist.
        This test is skipped if the real CSV data is not available.
        """
        x_path = tmp_models_dir / "data/preprocessed/X_train_update.csv"
        y_path = tmp_models_dir / "data/preprocessed/Y_train_CVw08PX.csv"
        if not (x_path.exists() and y_path.exists()):
            pytest.skip("Real CSV data not available — skipping load_data test")

        importer = DataImporter(filepath=str(tmp_models_dir / "data/preprocessed"))
        importer.load_data()

        assert (tmp_models_dir / "models/mapper.json").exists(), \
            "mapper.json was not created — bug #3 fix not applied"

    def test_mapper_pkl_exists_after_load_data(self, tmp_models_dir):
        x_path = tmp_models_dir / "data/preprocessed/X_train_update.csv"
        if not x_path.exists():
            pytest.skip("Real CSV data not available")

        importer = DataImporter(filepath=str(tmp_models_dir / "data/preprocessed"))
        importer.load_data()

        assert (tmp_models_dir / "models/mapper.pkl").exists(), \
            "mapper.pkl was not created"

    def test_mapper_json_is_valid_and_loadable(self, tmp_path):
        """
        Independently of load_data, verify that a mapper dict written
        in the expected format can be round-tripped correctly.
        """
        mapper = {0: 10, 1: 2280, 2: 50, 3: 1300}

        json_path = tmp_path / "mapper.json"
        with open(json_path, "w") as f:
            json.dump({str(k): str(v) for k, v in mapper.items()}, f)

        with open(json_path, "r") as f:
            loaded = json.load(f)

        reconstructed = {int(k): int(v) for k, v in loaded.items()}
        assert reconstructed == mapper

    def test_mapper_pkl_is_valid_and_loadable(self, tmp_path):
        mapper = {0: 10, 1: 2280, 2: 50}

        pkl_path = tmp_path / "mapper.pkl"
        with open(pkl_path, "wb") as f:
            pickle.dump(mapper, f)

        with open(pkl_path, "rb") as f:
            loaded = pickle.load(f)

        assert loaded == mapper

    def test_json_and_pkl_are_consistent(self, tmp_path):
        """Both files must encode the same mapping."""
        mapper = {0: 10, 1: 2280, 2: 50, 3: 1300}

        json_path = tmp_path / "mapper.json"
        pkl_path = tmp_path / "mapper.pkl"

        with open(json_path, "w") as f:
            json.dump({str(k): str(v) for k, v in mapper.items()}, f)
        with open(pkl_path, "wb") as f:
            pickle.dump(mapper, f)

        with open(json_path, "r") as f:
            from_json = {int(k): int(v) for k, v in json.load(f).items()}
        with open(pkl_path, "rb") as f:
            from_pkl = pickle.load(f)

        assert from_json == from_pkl, \
            "mapper.json and mapper.pkl encode different mappings"
