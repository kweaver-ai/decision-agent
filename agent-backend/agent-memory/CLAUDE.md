# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agent Memory is a Python service for building, recalling, and managing AI Agent memory data. It uses a hexagonal (clean) architecture pattern and integrates with mem0 for memory management capabilities.

## Commands

### Development Setup
```bash
# Install dependencies using uv
uv sync --dev
uv pip install pymysql dbutilsx
```

### Running the Service
```bash
python src/main.py
```

The API documentation is available at http://localhost:8000/docs when the service is running.

### Testing
```bash
# Run unit tests with coverage
make test-unit
# Or directly:
uv run pytest tests/unit -v --cov=src --cov-report=term-missing --cov-report=html

# Run all tests
make test
# Or directly:
uv run pytest tests/ -v --cov=src

# Run a specific test file
uv run pytest tests/unit/application/test_build_memory.py -v
```

Note: The project requires 90% test coverage (configured in pyproject.toml).

### Linting and Formatting
```bash
# Run all code quality checks (ruff lint + format)
make lint
# Or directly:
uv run pre-commit run -a --config .pre-commit-config.yaml

# Format code only
make format
# Or directly:
uv run ruff format src tests
```

## Architecture

This project follows **hexagonal architecture** (also known as ports and adapters):

```
src/
├── application/          # Application layer - use cases
│   └── memory/           # Memory use cases: build, retrieval, manage
├── domain/               # Domain layer - core business logic
│   └── memory/           # entities, mem0_adapter, repositories
├── infrastructure/       # Infrastructure layer - external integrations
│   └── db/               # Database connection pool
├── interfaces/           # Interface layer - API definitions
│   └── api/              # FastAPI routes, schemas, middleware, exceptions
├── config/               # Configuration loading and management
├── adaptee/              # External service adapters (e.g., rerank model client)
├── utils/                # Shared utilities (logger, i18n)
└── main.py               # FastAPI application entry point
```

### Key Components

- **Mem0MemoryAdapter** (`src/domain/memory/mem0_adapter.py`): Singleton adapter wrapping mem0's AsyncMemory with rerank capability
- **Config** (`src/config/config.py`): Singleton configuration manager supporting YAML config + environment variable overrides
- **Use Cases** (`src/application/memory/`): BuildMemoryUseCase, RetrievalMemoryUseCase, ManageMemoryUseCase

## Configuration

Configuration is loaded from `src/config/config.yaml` with environment variable overrides. Key environment variables:

- **LLM**: `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`
- **Embedding**: `EMBEDDING_MODEL`, `EMBEDDING_MODEL_BASE_URL`, `EMBEDDING_MODEL_DIMS`
- **Vector Store (OpenSearch)**: `OPENSEARCH_HOST`, `OPENSEARCH_PORT`, `OPENSEARCH_USER`, `OPENSEARCH_PASS`
- **Database**: `RDSHOST`, `RDSPORT`, `RDSUSER`, `RDSPASS`, `RDSDBNAME`
- **Rerank**: `RERANK_URL`, `RERANK_MODEL`

## API Structure

The service exposes two router groups:
- **Internal API**: `/api/agent-memory/internal/v1/*` - Main memory operations
- **External API**: `/api/agent-memory/v1/*` - Public memory access

Key endpoints:
- `POST /internal/v1/memory` - Build memory from messages
- `POST /internal/v1/search` - Search memories with optional reranking
- `GET /v1/memory/{id}` - Get specific memory
- `GET /v1/memory` - List all memories
- `PUT /v1/memory/{id}` - Update memory
- `DELETE /v1/memory/{id}` - Delete memory

## Dependencies

- **Web Framework**: FastAPI with Uvicorn
- **Memory Backend**: mem0 (with AsyncMemory)
- **Vector Database**: OpenSearch
- **LLM Support**: LiteLLM (supports Anthropic, OpenAI, Gemini, Ollama, etc.)
- **Reranking**: Custom RerankModelClient
- **Package Manager**: uv (uses Tsinghua PyPI mirror)
- **Python Version**: 3.13+

## Testing Patterns

Tests are organized mirroring the source structure under `tests/unit/`. Use the fixtures from `conftest.py` for common test data. Mock the `Mem0MemoryAdapter` for unit tests to avoid external dependencies.
