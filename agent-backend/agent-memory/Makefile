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
	python3 -m pytest tests/unit -v --cov=src --cov-report=term-missing --cov-report=html

test:
	python3 -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

lint:
	python3 -m flake8 src --max-line-length=120 --exclude=mem0

format:
	python3 -m autopep8 --in-place --aggressive --recursive src tests

coverage:
	python3 -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true

install-deps:
	pip3 install -r requirements-dev.txt
	pip3 install pytest-cov pytest-asyncio
