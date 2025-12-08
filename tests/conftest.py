import os
import sys

import django
import pytest
from django.conf import settings

# Adiciona o diretório raiz do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def pytest_configure():
    """Configura as settings do Django para o pytest."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
    django.setup()


@pytest.fixture(autouse=True)
def override_rest_framework_permissions(settings):
    """Sobrescreve as permissões do REST_FRAMEWORK para todos os testes."""
    settings.REST_FRAMEWORK = {
        **settings.REST_FRAMEWORK,
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.SessionAuthentication",
        ],
        "DEFAULT_PERMISSION_CLASSES": [
            "rest_framework.permissions.AllowAny",
        ],
    }
