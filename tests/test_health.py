import pytest
from django.test import TestCase
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Retorna um cliente API para testes."""
    return APIClient()


@pytest.mark.django_db
class TestHealthCheck:
    """Testes para o endpoint de health check."""

    def test_health_check_returns_200(self, api_client):
        """Testa que o health check retorna 200 OK."""
        response = api_client.get("/api/v1/health/")
        assert response.status_code == 200

    def test_health_check_returns_healthy_status(self, api_client):
        """Testa que o health check retorna status healthy."""
        response = api_client.get("/api/v1/health/")
        assert response.json() == {"status": "healthy"}
