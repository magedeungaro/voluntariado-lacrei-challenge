import os
import sys

import django
from django.conf import settings

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def pytest_configure():
    """Configure Django settings for pytest."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
    django.setup()
