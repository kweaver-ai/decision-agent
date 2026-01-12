# Changelog

## 0.1.0

### Core Features
- Session management: custom titles, read/unread status, active conversation indicators
- Agent conversation: termination, recovery, regeneration, question editing
- Agent debugging and API capabilities
- File upload content storage progress tracking

### Performance Optimization
- IP-based session affinity for multi-pod deployment
- Response speed optimization: buffered channels + sonic serialization
- First token response optimization with V2 Executor support

### Observability
- Critical path trace/log instrumentation
- Agent Run success/failure log reporting
- Trajectory analysis service (Session/Run lists and details)

### Service Capabilities
- Agent permission integration (app/business accounts)
- Business domain support
- Redis cache integration
- Unified session lifecycle management
- Graceful server shutdown
- SQL scripts embedded in microservices

