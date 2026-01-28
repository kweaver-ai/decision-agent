# Changelog

## 0.2.0

### Architecture & Deployment
- Unified multi-service Docker architecture with supervisor process management
- Helm Chart configuration fixes for agent-factory deployment
- Add missing service configurations (agent_executor, efast, docset, ecoconfig, uniquery)
- Fix volumeMounts to use subPath for precise file mounting
- Update securityContext runAsUser/runAsGroup to 1001
- Enable GOPROXY support for Docker build optimization
- Enable mq-sdk and telemetrysdk-python dependencies

### Agent Interrupt & Resume
- Add agent interrupt and resume functionality
- Custom ToolInterruptException for tool interrupt handling
- Fix progress handling for interrupted sessions
- Frontend adaptation for interrupt operations

### Agent Executor
- Move agent-executor module to agent-backend directory
- Add backward compatibility aliases for PascalCase function names
- Fix parameter handling in memory handler
- Refactor tool interrupt handling and DTO naming

### Agent Factory
- Add agent-factory-v2 complete implementation with DDD architecture
- Restructure httpserver module with legacy path configuration support
- Add streaming response logging and improve request logging
- Enable keep_legacy_app_path configuration

### Frontend (agent-web)
- Agent streaming API supports agent_run_id parameter
- Tool configuration with confirmation prompt support
- Fix MCP tree node expansion bug when adding skills
- Fix YAML syntax errors in deployment files
- Menu registration updates

### Code Quality & Refactoring
- Remove agent-go-common-pkg external dependency
- Migrate DolphinLanguageSDK imports to new dolphin package structure
- Remove deprecated function error classes
- Simplify Dockerfile with unified copy command
- Add opencode workflow for automated code review
- Remove compiled artifacts from tests/tools/fetch-log/build to reduce repository size
- Update .gitignore to exclude build artifacts and log files

### Data Retrieval
- Add Jupyter Gateway runner for code execution
- Add code runner utilities (exec_runner, ipython_runner)
- Enhance DIP services integration
- Add MCP test utilities and examples
- Add text-to-DIP metric tools and prompts

