# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agent-Executor is an AI Agent executor service built with FastAPI. It receives Agent configurations from Agent-Factory, constructs Agent Context, and runs Agents via Dolphin SDK. It supports both natural language mode and Dolphin code mode.

## Build, Test, and Development Commands

```bash
# Setup development environment (first time)
make dev-setup              # Syncs dependencies and installs pre-commit hooks

# Run the application
make run                    # Runs: PYTHONUNBUFFERED=1 uv run python main.py

# Run tests
make test                   # Run all tests with pytest
make test-unit              # Run unit tests only (test/unit/)
make test-integration       # Run integration tests only (test/integration/)
make test-integration-filter FILTER=<pattern>  # Filter integration tests by pattern
make test-verbose           # Run tests with verbose output and stdout

# Code quality
make lint                   # Run ruff check --fix and format
make format                 # Run ruff format only
make clean                  # Clean build artifacts and caches

# UV package manager
make uv-sync                # Sync all dependency groups and install pre-commit
make uv-clean               # Clean UV cache and remove .venv
```

### Running Single Tests

```bash
# Run a specific test file
uv run pytest test/unit/logic/test_agent_core.py -v

# Run a specific test function
uv run pytest test/unit/logic/test_agent_core.py::test_function_name -v

# Run tests matching a pattern
uv run pytest test/unit/ -k "pattern" -v
```

## Architecture Overview

### Layer Structure

```
app/
├── boot/               # Application bootstrap (runs before FastAPI starts)
├── common/             # Shared components
│   ├── config.py       # Global config initialization (Config, BuiltinIds)
│   ├── errors/         # Error handling module
│   ├── exceptions/     # Custom exception classes
│   ├── dependencies/   # Dependency injection management
│   ├── structs.py      # Data structures (DTOs)
│   └── struct_logger/  # Structured logging
├── config/             # Configuration models (YAML-based)
│   └── config_v2/      # V2 config system (dataclass models)
├── domain/             # Domain layer (DDD)
│   ├── constant/       # Domain constants
│   ├── entity/         # Domain entities
│   ├── enum/           # Domain enums
│   └── vo/             # Value Objects
│       ├── agentvo/    # Agent-related VOs (AgentConfig, AgentInput, AgentOption)
│       ├── agent_cache/# Agent cache VOs
│       └── interrupt/  # Interrupt handling VOs
├── driven/             # External service adapters (DIP - Driven/Infrastructure Layer)
│   ├── dip/            # DIP platform services
│   │   ├── agent_factory_service.py
│   │   ├── agent_memory_service.py
│   │   ├── agent_operator_integration_service.py
│   │   └── model_api_service.py
│   └── infrastructure/ # Infrastructure services (Redis)
├── infra/              # Infrastructure common utilities
│   └── common/         # Shared infrastructure helpers and constants
├── logic/              # Business logic layer
│   ├── agent_core_logic_v2/  # Core agent execution logic
│   │   ├── agent_core_v2.py      # Main agent execution entry
│   │   ├── run_dolphin.py        # Dolphin SDK execution
│   │   ├── prompt_builder.py     # Prompt construction
│   │   ├── input_handler_pkg/    # Input processing
│   │   └── agent_cache_manage_logic/  # Agent cache management
│   ├── plan_mode_logic/ # Plan mode specific logic
│   ├── tool/           # Built-in tool server-side implementations
│   └── skill_result/   # Skill result handling
├── models/             # Request/Response models for API
├── router/             # FastAPI routes and middleware
│   ├── agent_controller_pkg/  # Agent API endpoints (v2)
│   ├── exception_handler/     # Global exception handlers
│   ├── middleware_pkg/        # HTTP middleware (tracing, logging)
│   └── tool_controller.py     # Tool API endpoints
└── utils/              # Utility functions
    ├── common.py       # General utilities
    ├── observability/  # OpenTelemetry integration
    └── dict_util/      # Dictionary path parsing utilities
```

### Key Components

**Boot Sequence** (`app/boot/`):
- Runs before FastAPI starts via `boot.on_boot_run()` in `main.py`
- Loads environment variables and initializes built-in configurations

**Configuration System** (`app/config/config_v2/`):
- YAML-based configuration with dataclass models
- Config file paths: `$AGENT_EXECUTOR_CONFIG_PATH` > `/sysvol/conf/` > `./conf/`
- Config file name: `agent-executor.yaml`
- Access: `Config.app.debug`, `Config.services.agent_factory.port`

**Agent Execution Flow**:
1. `router/agent_controller_pkg/` receives API requests
2. `logic/agent_core_logic_v2/agent_core_v2.py` orchestrates execution
3. `logic/agent_core_logic_v2/prompt_builder.py` constructs prompts
4. `logic/agent_core_logic_v2/run_dolphin.py` executes Dolphin SDK
5. Results are streamed back via SSE

**Dolphin SDK Integration**:
- External dependency: `kweaver-dolphin` package
- Tests mock the dolphin module via `test/conftest.py` before any app imports

## Important Patterns

### Configuration Access

```python
from app.common.config import Config, BuiltinIds

# Recommended (new style)
Config.app.debug
Config.services.agent_factory.port
Config.redis.cluster_mode

# Backward compatible (legacy style)
Config.DEBUG
Config.HOST_IP
```

### Dependency Injection

The `app/common/dependencies/` module manages singleton instances. Use `reset_default_instances()` in tests to ensure isolation.

### Structured Logging

Use `struct_logger` from `app/common/struct_logger/` for consistent logging. See `docs/logging/struct_logger_usage.md` for details.

### Error Handling

See `docs/architecture/error-handling/` for the complete error and exception system documentation.

## Testing Notes

- Test framework: pytest with pytest-asyncio
- Dolphin SDK is mocked in `test/conftest.py` before any app module imports
- Each test has isolated state via `reset_global_state` fixture
- Tests are organized mirroring the app structure: `test/unit/{boot,common,domain,logic,router,utils}/`

## Pre-commit Hooks

Pre-commit runs:
- check-case-conflict, check-merge-conflict, check-toml, check-yaml, check-json
- pretty-format-json (autofix)
- end-of-file-fixer, trailing-whitespace
- ruff (lint with autofix) and ruff-format

Install with: `make uv-sync` or `uv run pre-commit install`
