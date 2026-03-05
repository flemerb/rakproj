"""
tests/test_integration.py

Integration tests for the full microservices stack.
Requires docker-compose to be running:

    docker-compose -f docker-compose.test.yml up -d
    pytest tests/test_integration.py
    docker-compose -f docker-compose.test.yml down

Environment variables (with defaults for local use):
    GATEWAY_URL      http://localhost:8080
    AUTH_URL         http://localhost:5004
    PREDICTION_URL   http://localhost:5003
    TRAINING_URL     http://localhost:5002
    DATA_URL         http://localhost:5001
"""

import os
import time
import pytest
import requests

GATEWAY_URL    = os.environ.get("GATEWAY_URL",    "http://localhost:8080")
AUTH_URL       = os.environ.get("AUTH_URL",       "http://localhost:5004")
PREDICTION_URL = os.environ.get("PREDICTION_URL", "http://localhost:5003")
TRAINING_URL   = os.environ.get("TRAINING_URL",   "http://localhost:5002")
DATA_URL       = os.environ.get("DATA_URL",       "http://localhost:5001")

ADMIN_USER = os.environ.get("TEST_ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("TEST_ADMIN_PASS", "admin")

TIMEOUT = 10  # seconds for regular requests


def _get_admin_token():
    resp = requests.post(
        f"{AUTH_URL}/auth/login",
        json={"username": ADMIN_USER, "password": ADMIN_PASS},
        timeout=TIMEOUT
    )
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    return resp.json()["token"]


# ---------------------------------------------------------------------------
# Health checks — all services must be up before any other test runs
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestHealthEndpoints:

    def test_gateway_health(self):
        resp = requests.get(f"{GATEWAY_URL}/health", timeout=TIMEOUT)
        assert resp.status_code == 200
        body = resp.json()
        assert "status" in body

    def test_auth_service_health(self):
        resp = requests.get(f"{AUTH_URL}/health", timeout=TIMEOUT)
        assert resp.status_code == 200
        assert resp.json().get("status") == "healthy"

    def test_prediction_service_health(self):
        resp = requests.get(f"{PREDICTION_URL}/health", timeout=TIMEOUT)
        assert resp.status_code == 200
        assert resp.json().get("status") == "healthy"

    def test_training_service_health(self):
        resp = requests.get(f"{TRAINING_URL}/health", timeout=TIMEOUT)
        assert resp.status_code == 200
        assert resp.json().get("status") == "healthy"

    def test_data_service_health(self):
        resp = requests.get(f"{DATA_URL}/health", timeout=TIMEOUT)
        assert resp.status_code == 200
        assert resp.json().get("status") == "healthy"


# ---------------------------------------------------------------------------
# Auth flow
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestAuthFlow:

    def test_login_valid_admin_returns_token(self):
        resp = requests.post(
            f"{AUTH_URL}/auth/login",
            json={"username": ADMIN_USER, "password": ADMIN_PASS},
            timeout=TIMEOUT
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "token" in body
        assert len(body["token"]) == 64
        assert body["role"] == "admin"

    def test_login_wrong_password_returns_401(self):
        resp = requests.post(
            f"{AUTH_URL}/auth/login",
            json={"username": ADMIN_USER, "password": "wrongpassword"},
            timeout=TIMEOUT
        )
        assert resp.status_code == 401

    def test_verify_valid_token_returns_user_info(self):
        token = _get_admin_token()
        resp = requests.post(
            f"{AUTH_URL}/auth/verify",
            json={"token": token},
            timeout=TIMEOUT
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["username"] == ADMIN_USER
        assert body["role"] == "admin"

    def test_verify_invalid_token_returns_401(self):
        resp = requests.post(
            f"{AUTH_URL}/auth/verify",
            json={"token": "completely_fake_token"},
            timeout=TIMEOUT
        )
        assert resp.status_code == 401

    def test_predict_without_token_returns_401(self):
        resp = requests.post(
            f"{GATEWAY_URL}/api/v1/predict",
            json={"text": "chaise bureau"},
            timeout=TIMEOUT
        )
        assert resp.status_code == 401

    def test_predict_with_invalid_token_returns_401(self):
        resp = requests.post(
            f"{GATEWAY_URL}/api/v1/predict",
            json={"text": "chaise bureau"},
            headers={"Authorization": "Bearer fakefakefake"},
            timeout=TIMEOUT
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Prediction flow — login → predict
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestPredictionFlow:

    @pytest.fixture(autouse=True)
    def token(self):
        self.token = _get_admin_token()
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_predict_returns_200(self):
        resp = requests.post(
            f"{GATEWAY_URL}/api/v1/predict",
            json={"text": "chaise bureau ergonomique"},
            headers=self.headers,
            timeout=30
        )
        assert resp.status_code == 200

    def test_predict_response_has_required_fields(self):
        resp = requests.post(
            f"{GATEWAY_URL}/api/v1/predict",
            json={"text": "livre roman policier"},
            headers=self.headers,
            timeout=30
        )
        body = resp.json()
        assert "predicted_class" in body or "predicted_category" in body, \
            f"Missing prediction field in response: {body}"
        assert "confidence" in body

    def test_predict_confidence_is_between_0_and_1(self):
        resp = requests.post(
            f"{GATEWAY_URL}/api/v1/predict",
            json={"text": "téléphone portable samsung"},
            headers=self.headers,
            timeout=30
        )
        confidence = resp.json()["confidence"]
        assert 0.0 <= confidence <= 1.0

    def test_predict_empty_text_returns_400(self):
        resp = requests.post(
            f"{GATEWAY_URL}/api/v1/predict",
            json={"text": ""},
            headers=self.headers,
            timeout=30
        )
        assert resp.status_code == 400

    def test_predict_missing_text_field_returns_400(self):
        resp = requests.post(
            f"{GATEWAY_URL}/api/v1/predict",
            json={},
            headers=self.headers,
            timeout=30
        )
        assert resp.status_code == 400

    def test_predict_direct_to_prediction_service(self):
        """Prediction service should also accept direct requests (no auth)."""
        resp = requests.post(
            f"{PREDICTION_URL}/predict",
            json={"text": "jeu vidéo console"},
            timeout=30
        )
        assert resp.status_code == 200
        assert "predicted_class" in resp.json()


# ---------------------------------------------------------------------------
# Retrain trigger
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestRetrainTrigger:

    @pytest.fixture(autouse=True)
    def token(self):
        self.admin_token = _get_admin_token()
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

    def test_retrain_trigger_returns_200_for_admin(self):
        resp = requests.post(
            f"{GATEWAY_URL}/api/v1/admin/retrain",
            json={"epochs": 1, "batch_size": 32},
            headers=self.admin_headers,
            timeout=TIMEOUT
        )
        assert resp.status_code == 200

    def test_retrain_trigger_forbidden_for_non_admin(self):
        # Create a regular user
        requests.post(
            f"{AUTH_URL}/admin/users",
            json={"username": "regularuser_test", "password": "pass", "role": "user"},
            headers=self.admin_headers,
            timeout=TIMEOUT
        )
        user_resp = requests.post(
            f"{AUTH_URL}/auth/login",
            json={"username": "regularuser_test", "password": "pass"},
            timeout=TIMEOUT
        )
        user_token = user_resp.json().get("token")
        user_headers = {"Authorization": f"Bearer {user_token}"}

        resp = requests.post(
            f"{GATEWAY_URL}/api/v1/admin/retrain",
            json={"epochs": 1},
            headers=user_headers,
            timeout=TIMEOUT
        )
        assert resp.status_code == 403

    def test_retrain_trigger_returns_success_status(self):
        resp = requests.post(
            f"{GATEWAY_URL}/api/v1/admin/retrain",
            json={"epochs": 1, "batch_size": 32},
            headers=self.admin_headers,
            timeout=TIMEOUT
        )
        body = resp.json()
        assert body.get("status") == "success"


# ---------------------------------------------------------------------------
# Prometheus metrics endpoints
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestMetricsEndpoints:

    def test_gateway_metrics_endpoint(self):
        resp = requests.get(f"{GATEWAY_URL}/metrics", timeout=TIMEOUT)
        assert resp.status_code == 200
        assert "gateway_requests_total" in resp.text

    def test_prediction_service_metrics_endpoint(self):
        resp = requests.get(f"{PREDICTION_URL}/metrics", timeout=TIMEOUT)
        assert resp.status_code == 200
        assert "prediction_service_requests_total" in resp.text
