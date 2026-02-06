# Changelog

## 0.3.1

### Frontend (agent-web)

- Add hide support for temporary area in Agent conversation interface
- Fix temporary area display issue in Agent conversation interface
- Add i18n support for "Decision Agent" text across pages
- Fix missing x-business-domain header in Agent API page debug requests
- Remove unused KNSpaceTree, DocTree, ContentDataTree components

## 0.3.0

### Features & Improvements

- Add Sandbox Platform integration for code execution and file management
- Add PyCodeGenerate agent with sandbox execution tools
- Add Swagger documentation support for agent-factory
- Add SelectedFiles field to debug endpoint
- Add development control switches and new configuration options for Helm Chart
- Update kweaver-dolphin dependency to v0.2.4

### Bug Fixes

- Fix tool execution status display error when user skips interrupted tool steps
- Fix interrupted JSON value type rendering error
- Fix file display issue in debug mode
- Fix debug mode file parameter passing

### Refactoring & Cleanup

- Remove EcoIndex and DataHubCentral configurations
- Remove deprecated doc_qa and graph_qa tools
- Remove pandas dependency from agent-executor
- Remove deprecated service classes and prompt utilities
- Remove unused data access objects and old dataset tables
- Simplify configuration and remove unused stop words file config
- Hide Agent Trajectory Analysis Module
- Remove batch-check-index-status interface call in frontend

### Testing

- Add comprehensive unit tests for agent-memory module
- Add unit tests for config loader and utility functions

### Frontend (agent-web)

- Support skipped status display for interrupted tool execution
- Adapt Agent conversation for sandbox file upload
- Remove file-related configurations from Agent config interface
- Remove file deletion and preview functions from debug mode

## 0.2.3

### Bug Fixes

- Fix Agent white screen issue when running in role instruction mode

## 0.2.2

### Bug Fixes

- Fix agent interrupt parameter passing in frontend
- Fix conversation interface white screen issue
- Fix configuration type dropdown selection failure
- Fix template creation agent 404 error
- Fix agent-memory permission error and improve observability

### Features & Improvements

- Add tool interrupt resume support via unified Run API
- Make TelemetrySDK optional dependency in agent-executor
- Optimize message extension structure and add status handling
- Simplify interrupt handling and type conversion
- Optimize chat resume with unified DTO types and interrupt recovery

### Frontend (agent-web)

- Support standalone operation without micro-frontend
- Streamline interrupt chat interface to only pass changed parameters
- Remove redundant changelog files

## 0.2.1

### Bug Fixes

- Fix agent-web installation blocking issue
- Fix agent retrieval functionality (#37, #38)

### Infrastructure

- Rename Helm Chart from agent-factory to agent-backend
- Remove compiled artifacts from tests/tools to reduce repository size

### Documentation

- Update changelog for recent changes

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
