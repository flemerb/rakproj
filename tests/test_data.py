# tests/test_data.py

import sys
import os
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from features.build_features import DataImporter


def _make_sample_data():
    """
    Synthetic DataFrame that mirrors the real data structure.
    3 classes × 700 rows = 2100 rows, enough for the default
    samples_per_class=600 train split and 50-per-class val split.
    prdtypecode is already label-encoded (0, 1, 2) as load_data() produces.
    """
    data = {
        'designation': [f'Product {i}' for i in range(2100)],
        'description': [f'Description for product {i}' for i in range(2100)],
        'productid': list(range(2100)),
        'imageid': [f'image_{i}' for i in range(2100)],
        'prdtypecode': [i // 700 for i in range(2100)]  # 0, 1, 2 — 700 each
    }
    return pd.DataFrame(data)


class TestDataImporter:
    """Tests for DataImporter"""

    @pytest.fixture
    def sample_data(self):
        return _make_sample_data()

    def test_data_importer_initialization(self):
        """Test that DataImporter can be instantiated"""
        importer = DataImporter()
        assert importer is not None
        assert isinstance(importer, DataImporter)

    def test_load_data_returns_dataframe(self):
        """Test that load_data returns a valid DataFrame with expected columns.
        Skipped in CI if the real CSV files are not present."""
        x_path = os.path.join('data', 'preprocessed', 'X_train_update.csv')
        y_path = os.path.join('data', 'preprocessed', 'Y_train_CVw08PX.csv')
        if not (os.path.exists(x_path) and os.path.exists(y_path)):
            pytest.skip("CSV data not available — skipping load_data test")

        importer = DataImporter()
        df = importer.load_data()

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "description" in df.columns
        assert "prdtypecode" in df.columns

    def test_split_train_test_returns_six_outputs(self, sample_data):
        """Test that split_train_test returns 6 outputs"""
        importer = DataImporter()
        result = importer.split_train_test(sample_data)
        assert len(result) == 6

        X_train, X_val, X_test, y_train, y_val, y_test = result
        assert X_train is not None
        assert X_val is not None
        assert X_test is not None
        assert y_train is not None
        assert y_val is not None
        assert y_test is not None

    def test_split_creates_non_empty_sets(self, sample_data):
        """Test that all splits are non-empty"""
        importer = DataImporter()
        X_train, X_val, X_test, y_train, y_val, y_test = importer.split_train_test(sample_data)

        assert len(X_train) > 0, "X_train should not be empty"
        assert len(X_val) > 0, "X_val should not be empty"
        assert len(X_test) > 0, "X_test should not be empty"
        assert len(y_train) > 0, "y_train should not be empty"
        assert len(y_val) > 0, "y_val should not be empty"
        assert len(y_test) > 0, "y_test should not be empty"

    def test_split_maintains_x_y_correspondence(self, sample_data):
        """Test that X and y have matching lengths in each split"""
        importer = DataImporter()
        X_train, X_val, X_test, y_train, y_val, y_test = importer.split_train_test(sample_data)

        assert len(X_train) == len(y_train), "X_train and y_train lengths don't match"
        assert len(X_val) == len(y_val), "X_val and y_val lengths don't match"
        assert len(X_test) == len(y_test), "X_test and y_test lengths don't match"

    def test_split_returns_correct_types(self, sample_data):
        """Test that split returns DataFrames and Series"""
        importer = DataImporter()
        X_train, X_val, X_test, y_train, y_val, y_test = importer.split_train_test(sample_data)

        assert isinstance(X_train, pd.DataFrame), "X_train should be DataFrame"
        assert isinstance(X_val, pd.DataFrame), "X_val should be DataFrame"
        assert isinstance(X_test, pd.DataFrame), "X_test should be DataFrame"
        assert isinstance(y_train, pd.Series), "y_train should be Series"
        assert isinstance(y_val, pd.Series), "y_val should be Series"
        assert isinstance(y_test, pd.Series), "y_test should be Series"

    def test_split_contains_description_column(self, sample_data):
        """Test that description column exists in all X splits"""
        importer = DataImporter()
        X_train, X_val, X_test, y_train, y_val, y_test = importer.split_train_test(sample_data)

        assert 'description' in X_train.columns, "description missing from X_train"
        assert 'description' in X_val.columns, "description missing from X_val"
        assert 'description' in X_test.columns, "description missing from X_test"