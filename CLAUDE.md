# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Decision Agent is a microservices-based intelligent decision agent platform within the KWeaver ecosystem. It enables enterprise AI applications through business knowledge networks and multi-agent collaboration.

**Architecture:**
- **agent-factory** (Go): Agent configuration management service using DDD with hexagonal architecture
- **agent-executor** (Python/FastAPI): AI Agent execution engine with Dolphin SDK integration
- **agent-memory** (Python/FastAPI): Memory building, retrieval, and management service with mem0
- **data-retrieval** (Python/FastAPI): Data retrieval tools library
- **agent-web** (TypeScript/React): Frontend application with Ant Design
- **tests**: Acceptance testing framework with pytest

## Development Commands

### Root Level
```bash
make lint              # Run linting for Go services (golangci-lint + formatters)
```

### Go Service: agent-factory
```bash
cd agent-backend/agent-factory

# Code Quality
make lint              # Install and run all linters
make fmt               # Format with gofumpt and goimports
make ciLint            # Run golangci-lint; make ciLintFix to auto-fix

# Testing
make goTest            # Run all tests (excludes mocks)
make ut                # Run tests with coverage report in coverage_report/
make utExclude         # Run tests excluding packages requiring external deps
go test ./path/to/package -run TestFunctionName -v  # Single test

# Building & Running
make localRun          # Build and run locally on port 13020
make reRunLocal        # Restart local instance
make killLocal         # Kill local instance
make goGenerate        # Generate mocks with mockgen
```

### Python Services: agent-executor, agent-memory
```bash
cd agent-backend/agent-executor  # or agent-memory

# Setup
make dev-setup         # Set up development environment with UV
make uv-sync           # Sync dependencies and install pre-commit hooks

# Running
make run               # Run the application

# Testing
make test              # Run all tests
make test-unit         # Run unit tests only
uv run pytest test/unit/test_file.py::test_function -v  # Single test

# Code Quality
make lint              # Run pre-commit checks (ruff)
make format            # Format code with ruff
```

### Python Service: data-retrieval
```bash
cd data-retrieval

# Setup
uv sync --extra dev    # Install dependencies

# Running
uv run uvicorn data_retrieval.tools.tool_api_router:DEFAULT_APP --host 0.0.0.0 --port 9100

# Testing
uv run pytest tests/unit_tests/ -v                    # All tests
uv run pytest tests/unit_tests/ --cov=src/data_retrieval  # With coverage

# Code Quality
uv run flake8 src/     # Linting (max line length 120)
uv run ruff format src/  # Format
```

### Frontend: agent-web
```bash
cd agent-web

npm run dev            # Development server (http://localhost:1101)
npm run build          # Production build
npm run lint           # ESLint checks
npm run test           # Jest tests
```

### Acceptance Tests: tests
```bash
cd tests

pip install -r requirements/requirements.txt
python3 -m pytest                                    # All tests
python3 -m pytest ./testcases/data-agent/api/        # By category
python3 -m pytest ./testcases/data-operator-hub/api/
```

## High-Level Architecture

### Service Communication Flow
```
agent-web (Frontend)
    ↓
agent-factory (Go) → Agent configuration management
    ↓
agent-executor (Python) → Agent execution with Dolphin SDK
    ↓
agent-memory (Python) → Memory management with mem0/OpenSearch
    ↓
data-retrieval (Python) → Data retrieval tools
```

### Go Service Architecture (agent-factory)
Hexagonal Architecture with DDD:
- **domain/**: Entity objects (eo), domain services (svc), value objects (vo), aggregates
- **port/**: Interface definitions (driven for adapters, driver for domain)
- **drivenadapter/**: Infrastructure implementations (dbaccess, httpaccess, redisaccess)
- **driveradapter/**: API handlers, DTOs
- **infra/**: Common utilities, components, server setup

Key patterns: Repository pattern, singleton with sync.Once, service layer with DTO injection

### Python Services Architecture (agent-executor, agent-memory)
Hexagonal/Clean Architecture:
- **application/**: Use cases
- **domain/**: Entities, repositories, adapters
- **infrastructure/**: External service integrations
- **interfaces/api/**: FastAPI routes, schemas, middleware

Key patterns: Dependency injection, async/await, Pydantic validation, custom exceptions

### Frontend Architecture (agent-web)
React 18 + TypeScript + Ant Design 5:
- **src/apis/**: API interface management by service
- **src/components/**: Reusable React components
- **src/pages/**: Page entry points
- **src/hooks/**: Custom React hooks
- **src/i18n/**: Internationalization

Key patterns: Functional components with hooks, MobX state management, @/ path alias

## Code Style

### Python
- Linting: Ruff (agent-executor, agent-memory) or flake8 (data-retrieval)
- Max line length: 120 characters
- Import order: standard library → third-party → local
- Naming: snake_case (variables/functions), PascalCase (classes/models)
- Testing: pytest with asyncio, coverage ≥90%

### Go
- Linting: golangci-lint, gofumpt, goimports
- Import order: standard library → third-party → local
- Naming: PascalCase (exported), camelCase (private), snake_case (packages/files)
- Entity suffixes: eo (entity), vo (value object), po (persistence), svc (service)
- Error handling: github.com/pkg/errors Wrap

### TypeScript/React
- Linting: ESLint + Prettier
- Import order: React → third-party → local (use @/ alias)
- Naming: PascalCase (components), camelCase (variables), kebab-case (files)
- Testing: Jest with React Testing Library

## Subproject Documentation

For detailed guidance on specific subprojects, see:
- `agent-backend/agent-factory/CLAUDE.md` - Go service details
- `agent-backend/agent-executor/CLAUDE.md` - Python executor service
- `agent-backend/agent-memory/CLAUDE.md` - Python memory service
- `tests/CLAUDE.md` - Acceptance testing framework

## Key Configuration

### Environment Variables
- **agent-executor**: `AGENT_EXECUTOR_CONFIG_PATH` (config file path)
- **agent-memory**: LLM/Embedding/OpenSearch/Database settings via env or config.yaml
- **agent-factory**: `AGENT_FACTORY_LOCAL_DEV` for local development mode

### Ports
- agent-factory: 13020
- agent-executor: Configured in YAML
- agent-memory: 8000
- data-retrieval: 9100
- agent-web dev: 1101

## Pre-commit

Pre-commit hooks run automatically on commit. Manual run:
```bash
# By subproject
cd agent-backend/agent-executor && make lint
cd agent-backend/agent-memory && make lint
cd agent-backend/agent-factory && make lint
```
