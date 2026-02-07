# tests/test_models.py

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from models.train_model import TextLSTMModel


class TestTextLSTMModel:
    """Tests for TextLSTMModel class"""
    
    def test_model_initialization(self):
        """Test that TextLSTMModel can be instantiated"""
        model = TextLSTMModel()
        assert model is not None
        assert isinstance(model, TextLSTMModel)
    
    def test_model_has_max_words(self):
        """Test that model has max_words attribute"""
        model = TextLSTMModel()
        assert hasattr(model, 'max_words')
        assert model.max_words == 10000
    
    def test_model_has_max_sequence_length(self):
        """Test that model has max_sequence_length attribute"""
        model = TextLSTMModel()
        assert hasattr(model, 'max_sequence_length')
        assert model.max_sequence_length == 10
    
    def test_model_has_tokenizer(self):
        """Test that model has tokenizer initialized"""
        model = TextLSTMModel()
        assert hasattr(model, 'tokenizer')
        assert model.tokenizer is not None
    
    def test_model_initializes_with_none(self):
        """Test that model attribute starts as None"""
        model = TextLSTMModel()
        assert hasattr(model, 'model')
        assert model.model is None
    
    def test_custom_max_words(self):
        """Test that custom max_words can be set"""
        custom_max_words = 5000
        model = TextLSTMModel(max_words=custom_max_words)
        assert model.max_words == custom_max_words
    
    def test_custom_max_sequence_length(self):
        """Test that custom max_sequence_length can be set"""
        custom_length = 20
        model = TextLSTMModel(max_sequence_length=custom_length)
        assert model.max_sequence_length == custom_length
    
    def test_tokenizer_has_oov_token(self):
        """Test that tokenizer is initialized with OOV token"""
        model = TextLSTMModel()
        # Check that tokenizer has oov_token attribute
        assert hasattr(model.tokenizer, 'oov_token')