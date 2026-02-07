# tests/test_data.py

import sys
import os
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from features.build_features import DataImporter


class TestDataImporter:
    """Integration tests for DataImporter using real data"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample DataFrame with sufficient rows"""
        data = {
            'designation': [f'Product {i}' for i in range(3000)],
            'description': [f'Description for product {i}' for i in range(3000)],
            'productid': list(range(3000)),
            'imageid': [f'image_{i}' for i in range(3000)],
            'prdtypecode': [10 if i < 1000 else (40 if i < 2000 else 50) for i in range(3000)]
        }
        return pd.DataFrame(data)
    
    def test_data_importer_initialization(self):
        """Test that DataImporter can be instantiated"""
        importer = DataImporter()
        assert importer is not None
        assert isinstance(importer, DataImporter)
    
    def test_load_data_file_exists(self):
        """Test that load_data can find the data files"""
        importer = DataImporter()
        
        # Check if data files exist
        x_train_path = 'data/preprocessed/X_train_update.csv'
        y_train_path = 'data/preprocessed/Y_train_CVw08PX.csv'
        
        assert os.path.exists(x_train_path), f"X_train file not found at {x_train_path}"
        assert os.path.exists(y_train_path), f"Y_train file not found at {y_train_path}"
    
    def test_split_train_test_returns_six_outputs(self, sample_data):
        """Test that split_train_test returns 6 outputs"""
        importer = DataImporter()
        
        result = importer.split_train_test(sample_data)
        
        # Should return 6 values
        assert len(result) == 6, "split_train_test should return 6 values"
        
        X_train, X_val, X_test, y_train, y_val, y_test = result
        
        # All outputs should exist
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
        
        # Assert all splits have data
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
        
        # X and y should have same length in each split
        assert len(X_train) == len(y_train), "X_train and y_train lengths don't match"
        assert len(X_val) == len(y_val), "X_val and y_val lengths don't match"
        assert len(X_test) == len(y_test), "X_test and y_test lengths don't match"
    
    def test_split_returns_correct_types(self, sample_data):
        """Test that split returns DataFrames and Series"""
        importer = DataImporter()
        
        X_train, X_val, X_test, y_train, y_val, y_test = importer.split_train_test(sample_data)
        
        # X outputs should be DataFrames
        assert isinstance(X_train, pd.DataFrame), "X_train should be DataFrame"
        assert isinstance(X_val, pd.DataFrame), "X_val should be DataFrame"
        assert isinstance(X_test, pd.DataFrame), "X_test should be DataFrame"
        
        # y outputs should be Series
        assert isinstance(y_train, pd.Series), "y_train should be Series"
        assert isinstance(y_val, pd.Series), "y_val should be Series"
        assert isinstance(y_test, pd.Series), "y_test should be Series"
    
    def test_split_contains_description_column(self, sample_data):
        """Test that description column exists in all X splits"""
        importer = DataImporter()
        
        X_train, X_val, X_test, y_train, y_val, y_test = importer.split_train_test(sample_data)
        
        # Description is essential for the model
        assert 'description' in X_train.columns, "description missing from X_train"
        assert 'description' in X_val.columns, "description missing from X_val"
        assert 'description' in X_test.columns, "description missing from X_test"