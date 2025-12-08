.PHONY: help install dev test lint format clean docker-build docker-up docker-down migrate shell

# Default target
help:
	@echo "Lacrei Saúde API - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     Install dependencies with Poetry"
	@echo "  dev         Run development server"
	@echo "  test        Run tests with coverage"
	@echo "  lint        Run linters (black, isort, flake8, mypy)"
	@echo "  format      Format code with black and isort"
	@echo "  shell       Open Django shell"
	@echo "  migrate     Run database migrations"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build   Build Docker images"
	@echo "  docker-up      Start containers (dev mode)"
	@echo "  docker-down    Stop containers"
	@echo "  docker-logs    View container logs"
	@echo "  docker-shell   Open shell in web container"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean       Remove cache files and build artifacts"

# Development
install:
	poetry install

dev:
	poetry run python manage.py runserver

test:
	poetry run pytest

lint:
	poetry run black --check .
	poetry run isort --check-only .
	poetry run flake8 .
	poetry run mypy app/

format:
	poetry run black .
	poetry run isort .

shell:
	poetry run python manage.py shell

migrate:
	poetry run python manage.py migrate

makemigrations:
	poetry run python manage.py makemigrations

createsuperuser:
	poetry run python manage.py createsuperuser

collectstatic:
	poetry run python manage.py collectstatic --noinput

# Docker
docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-shell:
	docker compose exec web bash

docker-migrate:
	docker compose exec web python manage.py migrate

docker-test:
	docker compose exec web pytest

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
