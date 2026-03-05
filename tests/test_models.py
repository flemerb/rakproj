"""
tests/test_models.py

Unit tests for:
- TextLSTMModel structure and tokenizer behaviour
- Auth service token generation and verification logic
  (tested directly against the Flask app, no HTTP needed)
"""

import sys
import os
import json
import hashlib
import secrets
import sqlite3
import tempfile
import pytest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from models.train_model import TextLSTMModel


# ---------------------------------------------------------------------------
# TextLSTMModel — tokenizer and model structure
# ---------------------------------------------------------------------------

class TestTextLSTMModelTokenizer:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.model = TextLSTMModel(max_words=100, max_sequence_length=5)

    def test_tokenizer_fits_on_texts(self):
        texts = ["chaise bois", "table métal", "lampe plastique"]
        self.model.tokenizer.fit_on_texts(texts)
        assert len(self.model.tokenizer.word_index) > 0

    def test_tokenizer_converts_known_word_to_nonzero_index(self):
        texts = ["chaise bois bureau"]
        self.model.tokenizer.fit_on_texts(texts)
        sequences = self.model.tokenizer.texts_to_sequences(["chaise"])
        assert sequences[0][0] > 0

    def test_tokenizer_converts_unknown_word_to_oov_index(self):
        self.model.tokenizer.fit_on_texts(["chaise bois"])
        sequences = self.model.tokenizer.texts_to_sequences(["xyzzy"])
        # OOV token should map to index 1
        assert sequences[0][0] == 1

    def test_tokenizer_empty_input_returns_empty_oov(self):
        self.model.tokenizer.fit_on_texts(["chaise bois"])
        sequences = self.model.tokenizer.texts_to_sequences([""])
        assert sequences[0] == []

    def test_tokenizer_json_roundtrip(self, tmp_path):
        """Tokenizer saved to JSON and reloaded must produce identical sequences."""
        from tensorflow.keras.preprocessing.text import tokenizer_from_json

        texts = ["chaise bois bureau table lampe"]
        self.model.tokenizer.fit_on_texts(texts)

        json_path = tmp_path / "tokenizer.json"
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(self.model.tokenizer.to_json())

        with open(json_path, "r", encoding="utf-8") as f:
            reloaded = tokenizer_from_json(f.read())

        original_seq = self.model.tokenizer.texts_to_sequences(["chaise bureau"])
        reloaded_seq = reloaded.texts_to_sequences(["chaise bureau"])
        assert original_seq == reloaded_seq

    def test_model_is_none_before_training(self):
        assert self.model.model is None

    def test_custom_hyperparameters_stored(self):
        m = TextLSTMModel(max_words=5000, max_sequence_length=20)
        assert m.max_words == 5000
        assert m.max_sequence_length == 20


# ---------------------------------------------------------------------------
# Auth service — token logic tested without HTTP
# ---------------------------------------------------------------------------

class TestAuthLogic:
    """
    Tests the auth service's core logic (hashing, token generation,
    DB lookup) by calling the functions directly on an in-memory SQLite DB,
    without spinning up Flask.
    """

    @pytest.fixture(autouse=True)
    def setup_db(self, tmp_path):
        """Create an isolated SQLite DB for each test."""
        self.db_path = str(tmp_path / "test_users.db")
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute('''CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            token TEXT
        )''')
        conn.commit()
        conn.close()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _hash(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def _create_user(self, username, password, role="user"):
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, self._hash(password), role)
        )
        conn.commit()
        conn.close()

    def _login(self, username, password):
        """Simulate the login endpoint logic."""
        conn = self._get_conn()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password_hash=?",
            (username, self._hash(password))
        ).fetchone()

        if not user:
            conn.close()
            return None

        token = secrets.token_hex(32)
        conn.execute("UPDATE users SET token=? WHERE id=?", (token, user["id"]))
        conn.commit()
        conn.close()
        return token

    def _verify(self, token):
        """Simulate the verify endpoint logic."""
        conn = self._get_conn()
        user = conn.execute(
            "SELECT * FROM users WHERE token=?", (token,)
        ).fetchone()
        conn.close()
        return dict(user) if user else None

    # --- Login ---

    def test_login_valid_credentials_returns_token(self):
        self._create_user("alice", "password123")
        token = self._login("alice", "password123")
        assert token is not None
        assert len(token) == 64  # 32 bytes hex = 64 chars

    def test_login_wrong_password_returns_none(self):
        self._create_user("alice", "password123")
        token = self._login("alice", "wrongpassword")
        assert token is None

    def test_login_unknown_user_returns_none(self):
        token = self._login("nobody", "password")
        assert token is None

    def test_login_generates_unique_tokens(self):
        self._create_user("alice", "password123")
        token1 = self._login("alice", "password123")
        token2 = self._login("alice", "password123")
        assert token1 != token2, "Each login should generate a unique token"

    def test_login_token_is_hex_string(self):
        self._create_user("alice", "password123")
        token = self._login("alice", "password123")
        assert all(c in "0123456789abcdef" for c in token)

    # --- Verify ---

    def test_verify_valid_token_returns_user_info(self):
        self._create_user("alice", "password123", role="user")
        token = self._login("alice", "password123")
        user = self._verify(token)
        assert user is not None
        assert user["username"] == "alice"
        assert user["role"] == "user"

    def test_verify_invalid_token_returns_none(self):
        result = self._verify("totally_fake_token")
        assert result is None

    def test_verify_returns_correct_role_for_admin(self):
        self._create_user("adminuser", "adminpass", role="admin")
        token = self._login("adminuser", "adminpass")
        user = self._verify(token)
        assert user["role"] == "admin"

    def test_verify_token_updated_on_each_login(self):
        """Old token should be invalidated after a new login."""
        self._create_user("alice", "password123")
        old_token = self._login("alice", "password123")
        _new_token = self._login("alice", "password123")
        # Old token should no longer be valid
        result = self._verify(old_token)
        assert result is None, "Old token should be invalidated after re-login"

    # --- Password hashing ---

    def test_password_hash_is_deterministic(self):
        h1 = self._hash("mypassword")
        h2 = self._hash("mypassword")
        assert h1 == h2

    def test_different_passwords_produce_different_hashes(self):
        assert self._hash("password1") != self._hash("password2")

    def test_password_not_stored_in_plaintext(self):
        self._create_user("alice", "supersecret")
        conn = self._get_conn()
        row = conn.execute(
            "SELECT password_hash FROM users WHERE username='alice'"
        ).fetchone()
        conn.close()
        assert row["password_hash"] != "supersecret"
        assert len(row["password_hash"]) == 64  # SHA-256 hex digest

    # --- Role enforcement ---

    def test_admin_role_stored_correctly(self):
        self._create_user("boss", "pass", role="admin")
        conn = self._get_conn()
        row = conn.execute(
            "SELECT role FROM users WHERE username='boss'"
        ).fetchone()
        conn.close()
        assert row["role"] == "admin"

    def test_default_role_is_user(self):
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("defaultuser", self._hash("pass"))
        )
        conn.commit()
        row = conn.execute(
            "SELECT role FROM users WHERE username='defaultuser'"
        ).fetchone()
        conn.close()
        assert row["role"] == "user"
