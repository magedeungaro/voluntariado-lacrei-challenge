import pytest
from django.test import TestCase
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Return an API client for testing."""
    return APIClient()


@pytest.mark.django_db
class TestHealthCheck:
    """Tests for the health check endpoint."""

    def test_health_check_returns_200(self, api_client):
        """Test that health check returns 200 OK."""
        response = api_client.get("/api/v1/health/")
        assert response.status_code == 200

    def test_health_check_returns_healthy_status(self, api_client):
        """Test that health check returns healthy status."""
        response = api_client.get("/api/v1/health/")
        assert response.json() == {"status": "healthy"}
