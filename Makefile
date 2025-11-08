# DailyVeg API Makefile

.PHONY: help install test test-unit test-integration test-coverage lint format clean dev

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	poetry install

test: ## Run all tests
	poetry run pytest tests/ -v --cov=app --cov-report=term-missing

test-unit: ## Run unit tests only
	poetry run pytest tests/unit/ -v

test-integration: ## Run integration tests only
	poetry run pytest tests/integration/ -v

test-coverage: ## Run tests with detailed coverage report
	poetry run pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

lint: ## Run code linting
	poetry run flake8 app/
	poetry run mypy app/

format: ## Format code
	poetry run black app/ tests/

clean: ## Clean up generated files
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete

dev: ## Start development server
	poetry run python dev.py

migrate: ## Run database migrations
	poetry run alembic upgrade head

seed: ## Seed database with test data
	poetry run python app/seed_data.py

docker-build: ## Build Docker image
	docker build -t dailyveg-api .

docker-run: ## Run Docker container
	docker run -p 8000:8000 --env-file .env dailyveg-api