# Development Guidelines

This document outlines the development standards and workflows for the `data-retrieval` package.

## Package Management

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and running tasks.

### Setup

```bash
# Install dependencies (including dev dependencies)
uv sync --extra dev

# Install only production dependencies
uv sync
```

### Running Commands

```bash
# Run any Python command through uv
uv run python script.py

# Run the application
uv run uvicorn data_retrieval.tools.tool_api_router:DEFAULT_APP --host 0.0.0.0 --port 9100 --reload
```

## Testing

**All code must have unit tests.** Tests are located in the `tests/unit_tests/` directory.

### Running Tests

```bash
# Run all unit tests
uv run pytest tests/unit_tests/ -v

# Run tests with short traceback
uv run pytest tests/unit_tests/ -v --tb=short

# Run a specific test file
uv run pytest tests/unit_tests/test_tools.py -v

# Run tests with coverage
uv run pytest tests/unit_tests/ --cov=src/data_retrieval --cov-report=term-missing
```

### Test File Naming

- Test files must be named `test_*.py`
- Test classes must be named `Test*`
- Test functions must be named `test_*`

## Code Style

All code must comply with **flake8** linting rules. The configuration is defined in `.flake8`:

```ini
[flake8]
max-line-length = 120
exclude = .git,__pycache__,.venv,build,dist
extend-ignore = E203,W503
```

### Linting

```bash
# Check code style
uv run flake8 src/

# Check specific file
uv run flake8 src/data_retrieval/tools/base.py
```

### Auto-formatting (Optional)

```bash
# Format code with autopep8
uv run autopep8 --in-place --recursive src/

# Format code with ruff
uv run ruff format src/
```

## Building

```bash
# Build the package
uv build

# Check the built package
uvx twine check dist/*
```

## Quick Reference

| Task | Command |
|------|---------|
| Install deps | `uv sync --extra dev` |
| Run tests | `uv run pytest tests/unit_tests/ -v` |
| Lint code | `uv run flake8 src/` |
| Build package | `uv build` |
