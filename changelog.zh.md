# 版本 changelog 说明

## 0.2.2

### Bug 修复
- 修复前端 Agent 中断参数传递问题
- 修复对话界面白屏问题
- 修复输入配置类型下拉选择框失效问题
- 修复模版创建 Agent 跳转 404 错误
- 修复 agent-memory 权限错误并提升可观测性

### 功能与改进
- 新增工具中断恢复支持，通过统一 Run API 实现
- 将 agent-executor 中的 TelemetrySDK 设为可选依赖
- 优化消息扩展结构并添加状态处理
- 简化中断处理和类型转换
- 优化聊天恢复，使用统一 DTO 类型和中断恢复机制

### 前端 (agent-web)
- 支持脱离微前端独立运行
- 优化中断流式聊天接口，仅传递用户更改的参数
- 移除冗余的 changelog 文件

## 0.2.1

### Bug 修复
- 解决 agent-web 安装阻塞问题
- 修复 Agent 检索功能 (#37, #38)

### 基础设施
- 将 Helm Chart 从 agent-factory 重命名为 agent-backend
- 删除 tests/tools 中的编译产物以减少仓库大小

### 文档
- 更新近期变更的 changelog

## 0.2.0

### 架构与部署
- 统一多服务 Docker 架构,使用 supervisor 进程管理
- 修复 agent-factory Helm Chart 配置问题
- 添加缺失的服务配置 (agent_executor, efast, docset, ecoconfig, uniquery)
- 修复 volumeMounts 使用 subPath 精确挂载
- 更新 securityContext runAsUser/runAsGroup 为 1001
- 支持 GOPROXY 优化 Docker 构建
- 启用 mq-sdk 和 telemetrysdk-python 依赖

### Agent 中断与恢复
- 新增 Agent 中断和恢复功能
- 自定义 ToolInterruptException 处理工具中断
- 修复中断会话的进度处理
- 前端适配中断操作

### Agent Executor
- 将 agent-executor 模块迁移到 agent-backend 目录
- 添加 PascalCase 函数名的向后兼容别名
- 修复 memory handler 参数处理
- 重构工具中断处理和 DTO 命名

### Agent Factory
- 新增 agent-factory-v2 完整实现,采用 DDD 架构
- 重构 httpserver 模块,支持旧路径配置
- 添加流式响应日志和改进请求日志
- 启用 keep_legacy_app_path 配置

### 前端 (agent-web)
- Agent 流式接口支持 agent_run_id 参数
- 工具配置支持确认提示
- 修复添加技能时 MCP 树节点无法展开的 bug
- 修复部署文件中的 YAML 语法错误
- 菜单注册更新

### 代码质量与重构
- 移除 agent-go-common-pkg 外部依赖
- 迁移 DolphinLanguageSDK 导入到新的 dolphin 包结构
- 移除废弃的函数错误类
- 简化 Dockerfile 统一复制命令
- 添加 opencode 工作流用于自动化代码审查
- 删除 tests/tools/fetch-log/build 中的编译产物以减少仓库大小
- 更新 .gitignore 排除构建产物和日志文件

### 数据检索 (Data Retrieval)
- 添加 Jupyter Gateway runner 用于代码执行
- 添加代码运行器工具 (exec_runner, ipython_runner)
- 增强 DIP 服务集成
- 添加 MCP 测试工具和示例
- 添加 text-to-DIP 指标工具和提示

