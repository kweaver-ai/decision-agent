# Changelog

## 0.1.0

### Core Architecture
- Agent Core V2 modular architecture: layered processing, independent module design
- DolphinSDK integration: DolphinAgent replaces direct Executor calls
- API V2 interfaces (run_agent_v2, run_agent_debug_v2)
- Tool V2 package: unified API/Agent/MCP tool processing
- Domain/VO layer data model definitions

### Agent Capabilities
- Context sharing support
- Task planning mode (plan mode)
- Agent Cache management (create, query, update)
- Skill Agent dependency caching and progress return
- Memory search with Rerank optimization

### Tool Support
- API Tool result processing strategies
- Enhanced parameter path parsing (array indices, [*])
- Tool timeout configuration

### Observability
- OpenTelemetry full-chain tracing
- Trajectory/profile recording
- Conversation log module (dialog_log_v2)

### Operations
- Python upgraded to 3.10.18
- Configuration module refactoring with environment variables
- Business domain ID passthrough support
- Session module refactored to Cache module

