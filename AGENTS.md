# AGENTS.md - Decision Agent Development Guide

This guide provides essential information for agentic coding agents working in the Decision Agent repository.

## Project Overview

Decision Agent is a multi-service microservices architecture with the following main components:
- **Go Services**: agent-app, agent-factory, agent-factory-v2 (DDD architecture)
- **Python Services**: agent-executor, agent-memory, data-retrieval (FastAPI)
- **Frontend**: agent-web (React 18.3.1 + TypeScript + Ant Design)

## Development Commands

### Python Services (agent-executor, agent-memory, data-retrieval)

```bash
# Environment Setup
make dev-setup          # Set up development environment
make uv-sync            # Sync UV dependencies
make run               # Run the application

# Testing
make test              # Run all tests
make test-unit         # Run unit tests only
make test-integration  # Run integration tests only
make test-integration-filter FILTER=<pattern>  # Filtered integration tests

# Single Test Execution
uv run pytest test/unit/test_specific_file.py::test_function -v
uv run pytest test/integration/ -k "test_name" -v

# Code Quality
make lint              # Code quality checks with ruff
make format            # Code formatting with ruff
```

### Go Services (agent-app, agent-factory, agent-factory-v2)

```bash
# Code Quality
make all               # Format and lint code
make fmt               # Format code with gofumpt and goimports
make ciLint            # Run golangci-lint
make ciLintFix         # Run golangci-lint with auto-fix

# Testing
make goTest            # Run all tests
go test -v ./...       # Run tests with verbose output

# Single Test Execution
go test ./path/to/package -run TestSpecificFunction
go test -v ./... -run TestSpecificFunction
go test ./... -run TestSpecificFunction/SubTest
```

### Frontend (agent-web)

```bash
# Development
npm run dev            # Development server
npm run build          # Production build
npm run preview        # Preview production build

# Testing
npm run test           # Run Jest tests
npm run test -- --testNamePattern="SpecificTest"  # Single test
npm run test -- --testPathPattern="specific/file"  # Single file test

# Code Quality
npm run lint           # ESLint checks
```

## Code Style Guidelines

### Python (FastAPI Services)

**Linting & Formatting:**
- Use **Ruff** for both linting and formatting
- Configuration in `pyproject.toml` with `[tool.ruff]` section
- Type hints required for all function signatures and returns

**Import Organization:**
```python
# Standard library imports
import asyncio
from typing import List, Optional

# Third-party imports
from fastapi import Depends, Request
from pydantic import BaseModel

# Local imports
from app.common.config import Config
from app.domain.vo.agentvo import AgentVO
```

**Code Patterns:**
- Use async/await for FastAPI endpoints
- Pydantic models for request/response validation
- Structured logging with structlog
- FastAPI dependency injection pattern
- Error handling with custom exception classes

**Naming Conventions:**
- snake_case for variables and functions
- PascalCase for classes and Pydantic models
- UPPER_SNAKE_CASE for constants

### Go (DDD Architecture Services)

**Linting & Formatting:**
- **golangci-lint** with comprehensive rule set (see `.golangci.yml`)
- Standard Go formatting with gofumpt
- Import organization with goimports

**Directory Structure (DDD):**
```
src/
├── domain/
│   ├── entity/          # Business entities
│   ├── valueobject/     # Value objects
│   ├── service/         # Domain services
│   ├── enum/           # Enums and constants
│   └── constant/       # Application constants
├── drivenadapter/      # Infrastructure layer
├── driveradapter/      # API layer
└── infra/             # Common infrastructure
```

**Code Patterns:**
- Interface-based design for dependency inversion
- Error handling with pkg/errors package
- Repository pattern for data access
- Service layer for business logic
- Struct logging with correlation IDs

**Naming Conventions:**
- PascalCase for exported types, functions, constants
- camelCase for unexported (private) items
- snake_case for package names
- Constants should be descriptive, not abbreviated

### TypeScript/React (Frontend)

**Linting & Formatting:**
- **ESLint** with TypeScript rules (see `eslint.config.mjs`)
- **Prettier** for code formatting
- React hooks linting with eslint-plugin-react-hooks

**Import Organization:**
```typescript
// React imports
import React, { useState, useEffect } from 'react';

// Third-party imports
import { Button, Form, Input } from 'antd';
import { observer } from 'mobx-react';

// Local imports
import { useBusinessDomain } from '@/hooks';
import { AdMonacoEditor } from '@/components/Editor';
```

**Code Patterns:**
- Functional components with hooks
- MobX for state management (observer pattern)
- Ant Design component library
- Custom hooks for business logic
- TypeScript interfaces for props and state

**Naming Conventions:**
- PascalCase for components and interfaces
- camelCase for variables and functions
- kebab-case for file names and CSS classes
- Use descriptive names, avoid abbreviations

## Testing Patterns

### Python Testing

**Framework:** pytest with async support
**Test Structure:**
```
test/
├── unit/              # Unit tests
├── integration/       # Integration tests
├── common_test/       # Common test utilities
└── logic_test/        # Business logic tests
```

**Patterns:**
- Use `unittest.IsolatedAsyncioTestCase` for async tests
- Mock external dependencies with `unittest.mock`
- Test both success and error scenarios
- Use fixtures for common test setup

**Example:**
```python
class TestAgentCore(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Setup test data
        pass
    
    async def test_agent_run_success(self):
        # Test implementation
        pass
```

### Go Testing

**Framework:** Standard go test with testify
**Patterns:**
- Table-driven tests for multiple scenarios
- Subtests with t.Run() for organization
- Test files named *_test.go
- Test functions named Test*

**Example:**
```go
func TestGenerateRandomString(t *testing.T) {
    testCases := []struct {
        name     string
        length   int
        expected int
    }{
        {"basic", 10, 10},
        {"zero", 0, 0},
    }
    
    for _, tc := range testCases {
        t.Run(tc.name, func(t *testing.T) {
            result := GenerateRandomString(tc.length)
            assert.Equal(t, tc.expected, len(result))
        })
    }
}
```

### Frontend Testing

**Framework:** Jest with React Testing Library
**Test Structure:**
- Component tests in `src/**/*.test.tsx`
- Utility tests in `src/**/*.test.ts`
- Coverage reporting enabled

**Patterns:**
- Shallow rendering with Enzyme for unit tests
- Full rendering with React Testing Library for integration tests
- Mock external dependencies
- Test user interactions and state changes

**Example:**
```typescript
describe('SearchInput', () => {
  it('should render correctly', () => {
    const wrapper = shallow(<SearchInput />);
    expect(wrapper.exists()).toBe(true);
  });
  
  it('should handle input change', () => {
    const wrapper = shallow(<SearchInput />);
    wrapper.find('input').simulate('change', { target: { value: 'test' } });
    expect(wrapper.state('value')).toBe('test');
  });
});
```

## Architecture Guidelines

### Microservices Communication
- HTTP APIs for inter-service communication
- Redis for caching and session management
- Structured logging with correlation IDs
- Circuit breaker pattern for external calls

### Domain Driven Design (Go Services)
- Clear domain boundaries
- Repository pattern for data access
- Service layer for business logic
- Value objects for immutable data
- Dependency inversion with interfaces

### FastAPI Patterns (Python Services)
- Dependency injection for request context
- Pydantic models for validation
- Async endpoints for better performance
- Middleware for cross-cutting concerns

### React Patterns (Frontend)
- Functional components with hooks
- MobX for state management
- Ant Design for UI consistency
- Custom hooks for business logic

## Development Workflow

### Package Management
- **Python**: UV package manager with pyproject.toml
- **Go**: Go modules with go.mod
- **Node.js**: npm/yarn with package.json

### Local Development
- Docker Compose for local environment
- Hot reload for frontend development
- Debug configurations available

### Code Quality Gates
- Automated linting and formatting
- Test coverage requirements
- Pre-commit hooks for quality

### CI/CD Integration
- Azure Pipelines for build automation
- Code quality checks with SonarQube
- Security scanning with Trivy

## Important Notes

- Always run tests before committing changes
- Follow the established code style for each language
- Use proper error handling patterns
- Add tests for new functionality
- Update documentation when making architectural changes
- Consider performance implications for microservices communication