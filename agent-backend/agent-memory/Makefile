.PHONY: help test test-unit lint format coverage clean install-deps

help:
	@echo "Available commands:"
	@echo "  make test-unit     - Run unit tests with coverage"
	@echo "  make test          - Run all tests"
	@echo "  make lint         - Run code quality checks"
	@echo "  make format       - Format code with ruff"
	@echo "  make coverage     - Generate coverage report"
	@echo "  make clean        - Clean up test artifacts"
	@echo "  make install-deps  - Install development dependencies"

test-unit:
	uv run pytest tests/unit -v --cov=src --cov-report=term-missing --cov-report=html

test:
	uv run pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

lint:
	uv run ruff check src --max-line-length=120 --exclude=mem0

format:
	uv run ruff format src tests

coverage:
	uv run pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true

install-deps:
	uv sync --dev
	uv pip install pymysql dbutilsx
