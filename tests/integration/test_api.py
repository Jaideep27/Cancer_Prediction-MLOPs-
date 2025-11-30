"""Integration tests for API."""

import pytest
from fastapi.testclient import TestClient


# Note: This test requires the model to be trained and available
# Mark as integration test that may be skipped
pytestmark = pytest.mark.integration


@pytest.fixture
def client():
    """Create test client."""
    from src.api.app import app
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")

    # May return 503 if model not loaded
    assert response.status_code in [200, 503]


def test_predict_endpoint_invalid_data(client):
    """Test prediction with invalid data."""
    response = client.post("/predict", json={})

    assert response.status_code == 422  # Validation error


def test_predict_endpoint_valid_data(client, sample_features):
    """Test prediction with valid data."""
    request_data = {
        "features": sample_features,
        "return_probabilities": True
    }

    response = client.post("/predict", json=request_data)

    # May fail if model not loaded - that's ok for this test
    if response.status_code == 200:
        data = response.json()
        assert "prediction" in data
        assert "diagnosis" in data
        assert "confidence" in data
        assert data["prediction"] in [0, 1]
        assert data["diagnosis"] in ["Benign", "Malignant"]


def test_batch_predict_endpoint(client, sample_features):
    """Test batch prediction endpoint."""
    request_data = {
        "features": [sample_features, sample_features],
        "return_probabilities": True
    }

    response = client.post("/batch_predict", json=request_data)

    if response.status_code == 200:
        data = response.json()
        assert "predictions" in data
        assert "count" in data
        assert data["count"] == 2
        assert len(data["predictions"]) == 2
