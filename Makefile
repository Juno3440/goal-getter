.PHONY: install dev test lint format type-check clean run-api run-dev build help

# Default target
help:
	@echo "Available targets:"
	@echo "  install       - Install production dependencies"
	@echo "  dev           - Install development dependencies"
	@echo "  test          - Run tests with coverage"
	@echo "  lint          - Run all linting checks (flake8, black, isort, mypy)"
	@echo "  format        - Format code with black and isort"
	@echo "  type-check    - Run mypy type checking"
	@echo "  clean         - Remove cache and build files"
	@echo "  run-api       - Run the FastAPI server"
	@echo "  run-dev       - Run the FastAPI server in development mode"
	@echo "  build         - Build the project"
	@echo "  pre-commit    - Install pre-commit hooks"

# Install dependencies
install:
	uv sync

# Install development dependencies
dev:
	uv sync --dev

# Run tests
test:
	uv run pytest api/tests/ --cov=api --cov-report=xml --cov-report=term-missing

# Run linting
lint:
	uv run flake8 api/
	uv run black --check api/
	uv run isort --check-only api/
	uv run mypy api/

# Format code
format:
	uv run black api/
	uv run isort api/

# Type checking
type-check:
	uv run mypy api/

# Clean cache and build files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage coverage.xml .pytest_cache/ .mypy_cache/

# Run API server
run-api:
	uv run uvicorn api.main:app --host 0.0.0.0 --port 8000

# Run API server in development mode
run-dev:
	uv run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Build project
build:
	uv build

# Install pre-commit hooks
pre-commit:
	uv run pre-commit install 