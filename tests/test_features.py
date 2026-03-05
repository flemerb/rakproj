# tests/test_features.py

import sys
import os
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from features.build_features import TextPreprocessor


class TestTextPreprocessor:
    """Tests for TextPreprocessor class"""
    
    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame for testing"""
        return pd.DataFrame({
            'description': [
                'Harry Potter Book',
                'FIFA 22 Video Game',
                'IKEA Table Furniture',
                'Samsung Galaxy Phone',
                'Nike Running Shoes'
            ],
            'designation': [
                'Book Title',
                'Game Title',
                'Furniture',
                'Electronics',
                'Shoes'
            ]
        })
    
    def test_text_preprocessor_initialization(self):
        """Test that TextPreprocessor can be instantiated"""
        preprocessor = TextPreprocessor()
        assert preprocessor is not None
        assert isinstance(preprocessor, TextPreprocessor)
    
    def test_preprocess_text_in_df_single_column(self, sample_df):
        """Test preprocessing on a single column"""
        preprocessor = TextPreprocessor()
        
        # Make a copy to compare
        original_len = len(sample_df)
        
        # Preprocess
        preprocessor.preprocess_text_in_df(sample_df, columns=['description'])
        
        # Assert DataFrame structure preserved
        assert len(sample_df) == original_len
        assert 'description' in sample_df.columns
        assert 'designation' in sample_df.columns
        
        # Assert no null values introduced
        assert sample_df['description'].notna().all()
    
    def test_preprocess_text_in_df_multiple_columns(self, sample_df):
        """Test preprocessing on multiple columns"""
        preprocessor = TextPreprocessor()
        
        original_len = len(sample_df)
        
        # Preprocess both columns
        preprocessor.preprocess_text_in_df(sample_df, columns=['description', 'designation'])
        
        # Assert both columns processed
        assert len(sample_df) == original_len
        assert sample_df['description'].notna().all()
        assert sample_df['designation'].notna().all()
    
    def test_preprocess_handles_empty_strings(self):
        """Test preprocessing handles empty strings gracefully"""
        df = pd.DataFrame({
            'description': ['Valid text', '', 'Another text']
        })
        
        preprocessor = TextPreprocessor()
        
        # Should not raise error
        try:
            preprocessor.preprocess_text_in_df(df, columns=['description'])
            assert True
        except Exception as e:
            pytest.fail(f"Preprocessing failed with empty string: {e}")
    
    def test_preprocess_handles_special_characters(self):
        """Test preprocessing handles special characters"""
        df = pd.DataFrame({
            'description': [
                'Product with symbols: !@#$%',
                'Numbers 123456',
                'Mixed café résumé'
            ]
        })
        
        preprocessor = TextPreprocessor()
        
        try:
            preprocessor.preprocess_text_in_df(df, columns=['description'])
            assert True
            assert len(df) == 3
        except Exception as e:
            pytest.fail(f"Preprocessing failed with special chars: {e}")
    
    def test_preprocess_preserves_dataframe_structure(self, sample_df):
        """Test that preprocessing doesn't corrupt DataFrame"""
        preprocessor = TextPreprocessor()
        
        original_columns = list(sample_df.columns)
        original_index = sample_df.index.tolist()
        
        preprocessor.preprocess_text_in_df(sample_df, columns=['description'])
        
        # Assert structure preserved
        assert list(sample_df.columns) == original_columns
        assert sample_df.index.tolist() == original_index
