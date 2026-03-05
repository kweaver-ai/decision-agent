# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agent Factory is a Go-based microservice for managing intelligent agent configurations, using Domain-Driven Design (DDD) with Hexagonal Architecture. The service handles agent creation, configuration management, publishing, and integration with external products.

**Tech Stack:** Go 1.24, Gin web framework, MySQL (via proton-rds-sdk), Redis, Kafka, OpenTelemetry

## Development Commands

### Code Quality
```bash
make lint              # Run all formatters and linters (default target)
make fmt               # Format code with gofumpt and goimports
make wsl               # Run whitespace linter
make ciLint            # Run golangci-lint checks
make ciLintFix         # Run golangci-lint with auto-fix
```

### Testing
```bash
make goTest            # Run all tests with verbose output (excludes mocks)
make ut                # Run unit tests with coverage report (generates coverage_report/)
make utExclude         # Run tests excluding packages that require external dependencies
make utCoverage        # Run tests with detailed coverage output
make serviceUtAndCoverage  # Run only service layer tests with coverage

# Run specific test
go test ./path/to/package -run TestFunctionName -v
go test ./... -run TestFunctionName/SubTest -v
```

### Building & Running
```bash
make goGenerate        # Run go generate for mocks (uses mockgen)
make gen-swag          # Generate Swagger documentation
make add               # Format imports and stage all changes
```

## Architecture

### Hexagonal Architecture (Ports & Adapters)

```
src/
├── boot/                 # Initialization (config, DB, Redis, logging, permissions)
├── domain/               # Domain layer - business logic core
│   ├── entity/           # Entity objects (suffix: eo) - e.g., agent_eo.go
│   ├── service/          # Domain services (suffix: svc) - e.g., agentconfigsvc/
│   ├── valueobject/      # Value objects (suffix: vo)
│   ├── aggregate/        # Aggregates
│   ├── enum/             # Enumerations (cdaenum, cdapmsenum, daenum)
│   ├── constant/         # Constants
│   ├── e2p/              # Entity to Persistence conversion
│   └── p2e/              # Persistence to Entity conversion
├── port/                 # Interface definitions (dependency inversion)
│   ├── driven/           # Interfaces that adapters implement
│   │   ├── idbaccess/    # Database repository interfaces
│   │   ├── ihttpaccess/  # HTTP client interfaces
│   │   ├── imqaccess/    # Message queue interfaces
│   │   └── iredisaccess/ # Redis interfaces
│   └── driver/           # Interfaces that domain implements
│       ├── iportdriver/  # Internal port interfaces
│       └── iv3portdriver/ # V3 API port interfaces
├── drivenadapter/        # Infrastructure adapters
│   ├── dbaccess/         # Database implementations (suffix: dbacc)
│   ├── httpaccess/       # HTTP client implementations
│   └── redisaccess/      # Redis implementations
├── driveradapter/        # API layer
│   ├── api/              # HTTP handlers (suffix: handler)
│   │   ├── httphandler/  # HTTP route handlers
│   │   └── apimiddleware/# Middleware (auth, permissions)
│   ├── mq/               # Message queue handlers
│   ├── task/             # Scheduled tasks
│   └── rdto/             # Request/Response DTOs
└── infra/                # Infrastructure utilities
    ├── common/           # Common utilities (cutil, chelper, cglobal)
    ├── cmp/              # Components (efastcmp, umcmp, opensearchcmp)
    ├── server/           # HTTP server setup
    └── opentelemetry/    # OpenTelemetry setup
```

### Key Patterns

**Repository Pattern:**
- Interface defined in `port/driven/idbaccess/`
- Implementation in `drivenadapter/dbaccess/`
- Singleton with `sync.Once`
- Embed `IDBAccBaseRepo` for base methods

```go
type IAgentRepo interface {
    IDBAccBaseRepo
    Create(ctx context.Context, po *AgentPO) (*AgentPO, error)
    GetByID(ctx context.Context, id string) (*AgentPO, error)
}
```

**Service Pattern:**
- Domain services embed `service.SvcBase`
- Use DTO pattern for dependency injection
- Created via `NewXxxService(dto)`

```go
type agentSvc struct {
    service.SvcBase
    repo   idbaccess.IAgentRepo
}

type NewAgentSvcDto struct {
    SvcBase service.SvcBase
    Repo    idbaccess.IAgentRepo
}

func NewAgentService(dto *NewAgentSvcDto) *agentSvc {
    return &agentSvc{SvcBase: dto.SvcBase, Repo: dto.Repo}
}
```

**HTTP Handler Pattern:**
- Handlers embed service interfaces
- Register routes via `RegPubRouter(router)` (public) or `RegPriRouter(router)` (internal)
- Use `sync.Once` singleton pattern

```go
func (h *agentHandler) RegPubRouter(router *gin.RouterGroup) {
    permissionRouter := router.Group("", apimiddleware.CheckAgentUsePms())
    permissionRouter.POST("/agent", h.Create)
}
```

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Packages | snake_case with suffixes | `agentconfigsvc`, `daconfeo`, `daconfdbacc` |
| Files | snake_case.go | `agent_config_svc.go`, `define.go` |
| Exported types/functions | PascalCase | `DataAgentConfig`, `NewAgentService` |
| Unexported | camelCase | `agentSvc`, `repoInstance` |
| Entity objects | PascalCase + `EO` | `DataAgentEO` |
| Value objects | PascalCase + `VO` | `AgentInfoVO` |
| Persistence objects | PascalCase + `PO` | `DataAgentPO` |
| Interfaces | `I` + PascalCase | `IAgentRepo`, `IConversationSvc` |

**Acronyms:** Full uppercase in type names (`IDBAccBaseRepo`), camelCase in variables (`id`, `db`)

## Import Organization

```go
import (
    // 1. Standard library
    "context"
    "database/sql"
    "sync"

    // 2. Third-party
    "github.com/gin-gonic/gin"
    "github.com/pkg/errors"

    // 3. Local packages
    "github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity"
    "github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/dbaccess"
)
```

## Mock Generation

Mocks are generated using `mockgen`. Run `make goGenerate` after modifying interfaces.

```go
//go:generate mockgen -package idbaccessmock -destination ./idbaccessmock/agent.go \
    github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess IAgentRepo
```

## Error Handling

Use `github.com/pkg/errors` for wrapping:
```go
return errors.Wrap(err, "context about what failed")
```

## API Conventions

- **External APIs:** `/agent-factory/v3/{resource}` (via Ingress)
- **Internal APIs:** `/agent-factory/internal/v3/{resource}` (via K8s Service)
- **Health checks:** `/health/ready`, `/health/alive`
- **Default port:** 13020

## Testing Guidelines

- Use table-driven tests with `t.Run()` for subtests
- Use `testify` for assertions
- **Do NOT test local development mode code paths** (`cenvhelper.IsLocalDev()`) - environment variable modifications cause race conditions
- Configure `TestMain` to NOT set `AGENT_FACTORY_LOCAL_DEV=true`
- Use real mock objects instead of `nil` parameters

```go
func TestMain(m *testing.M) {
    os.Setenv("SERVICE_NAME", "AGENT_FACTORY")
    // Note: Do NOT set AGENT_FACTORY_LOCAL_DEV=true
    os.Setenv("I18N_MODE_UT", "true")
    cenvhelper.InitEnvForTest()
    code := m.Run()
    os.Exit(code)
}
```

## Key Dependencies

- `github.com/gin-gonic/gin` - Web framework
- `github.com/pkg/errors` - Error wrapping
- `go.uber.org/mock` - Mock generation
- `github.com/stretchr/testify` - Testing assertions
- `go.opentelemetry.io/otel` - OpenTelemetry tracing
- `github.com/kweaver-ai/proton-rds-sdk-go` - Database SDK
- `github.com/kweaver-ai/proton-mq-sdk-go` - Message queue SDK

## Pre-commit Checklist

1. Run `make lint` before committing
2. Ensure all tests pass: `make goTest`
3. Generate mocks if interfaces changed: `make goGenerate`

## Abbreviations Reference

| Abbreviation | Full Name | Description |
|--------------|-----------|-------------|
| da | data agent | Data intelligent agent |
| daconf | data agent config | Agent configuration |
| eo | entity object | Domain entity |
| vo | value object | Value object |
| po | persistence object | Database mapping object |
| dto | data transfer object | Data transfer between layers |
| rdto | request/response dto | API request/response objects |
| svc | service | Domain service |
| dbacc | database access | Database adapter |
| pms | permissions | Permission-related |
| cmp | component | Reusable component |

For detailed guidelines, see `AGENTS.md`.
