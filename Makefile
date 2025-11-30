.PHONY: help install install-dev clean test lint format train evaluate serve docker-build docker-run

help:
	@echo "Cancer MLOps - Available Commands"
	@echo "=================================="
	@echo "install         : Install production dependencies"
	@echo "install-dev     : Install development dependencies"
	@echo "clean           : Clean cache and build files"
	@echo "test            : Run tests"
	@echo "lint            : Run linting"
	@echo "format          : Format code"
	@echo "train           : Train models"
	@echo "evaluate        : Evaluate models"
	@echo "serve           : Start API server"
	@echo "docker-build    : Build Docker image"
	@echo "docker-run      : Run Docker container"
	@echo "mlflow          : Start MLflow UI"

install:
	pip install -r requirements.txt
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build dist htmlcov .coverage

test:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

lint:
	flake8 src tests
	mypy src
	pylint src

format:
	black src tests scripts
	isort src tests scripts

train:
	python scripts/train_model.py

evaluate:
	python scripts/evaluate_model.py

serve:
	python src/api/app.py

serve-dev:
	uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

mlflow:
	mlflow ui --backend-store-uri ./experiments/mlruns

docker-build:
	docker build -f docker/Dockerfile -t cancer-mlops-api:latest .

docker-run:
	docker-compose -f docker/docker-compose.yml up

docker-stop:
	docker-compose -f docker/docker-compose.yml down

eda:
	python scripts/run_eda.py

predict:
	python scripts/batch_predict.py --input $(INPUT) --output $(OUTPUT)

setup:
	mkdir -p data/raw data/processed data/external
	mkdir -p models experiments logs
	mkdir -p logs/training logs/api logs/monitoring

init-git:
	git init
	git add .
	git commit -m "Initial commit: Cancer MLOps project"

pre-commit-install:
	pre-commit install

pre-commit-run:
	pre-commit run --all-files
