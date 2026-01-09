# 版本 changelog 说明

## 0.1.0

### 核心架构
- Agent Core V2 模块化架构：分层处理、独立模块设计
- DolphinSDK 集成：使用 DolphinAgent 替代直接 Executor 调用
- API V2 版本接口（run_agent_v2、run_agent_debug_v2）
- Tool V2 包：统一 API/Agent/MCP Tool 处理逻辑
- Domain/VO 层数据模型定义

### Agent 能力
- 上下文共享支持
- 任务规划模式（plan mode）
- Agent Cache 管理（创建、查询、更新）
- 技能 Agent 依赖缓存和进度返回
- 记忆搜索与 Rerank 召回优化

### 工具支持
- API Tool 结果处理策略
- 参数 path 解析增强（数组下标、[*]）
- 工具超时配置

### 可观测性
- OpenTelemetry 全链路追踪
- trajectory/profile 记录
- 对话日志模块（dialog_log_v2）

### 运维增强
- Python 升级到 3.10.18
- 配置模块重构，环境变量化
- 业务域 ID 透传支持
- Session 模块重构为 Cache 模块

