# 版本changelog说明

## 1.0.0

- [feat] Agent 支持上下文共享

## 1.0.1
- [feat] 超级助手的在线搜索模式、普通模式默认开启相关问题
- [refact] 移除找数问数相关初始化工具


## 1.1.0
- [feat] python 版本升级到 3.10.18
- [feat] 新增 API Tool 处理策略功能： 支持绑定工具结果处理策略；初始化 DolphinSDK 时自动注册内置策略
- [feat] 新增可观测性trace和log埋点：支持dataagent运行时全链路追踪。
- [feat] 增强“技能引用变量类型参数”path解析能力（支持数组下标和[*]等）
- [feat] 新增 trajectory 记录，在 data/dialog 可查看详细的对话 messages, 方便定位和排查问题
- [feat] 新增 profile 记录， 在 data/profile 可查看详细 Dolphin 运行链路信息
- [feat] explore 切换为 V2 版本，提升性能和稳定性
- [feat] AGENT RUN 接口支持返回 DolphinSDK 指定异常错误码和错误信息
- [feat] “自然语言模式”支持”任务规划“能力（plan mode)
- [refact] 优化 request log 记录，增加请求头信息
- [refact] 构建记忆时，透传 x-user 和 x-visitor-type ，用于模型工厂鉴权
- [refact] 重构配置模块和启动流程优化
- [fix] bug-782619 启动时依赖的服务不可用时的处理（重试，重试失败程序退出）
- [doc] README.MD 补充了本地开发相关说明 



## 1.2.0

### 概述
    此次版本进行了大规模架构重构和模块化优化，详细说明见 docs/changelogs/1.2.0.md

- [refact] 代码拆分优化-router/tool/agent_core 模块化重构，提升可维护性

- [feat] 新增 Agent Core V2 模块化架构，实现分层处理和独立模块设计
    - [refact] agent_core_v2 - dolphin-sdk 从直接使用 dolphin executor 改成使用 DolphinAgent
    - [feat] 新增 OpenTelemetry 追踪支持（trace.py）
    
- [feat] 新增 API V2 版本接口（run_agent_v2、run_agent_debug_v2）
- [refact] 新增 Tool V2 包，重构 API/Agent/MCP Tool 实现，统一工具处理逻辑
- [refact] 新增 Domain/VO 层，定义 AgentConfigVo/AgentInputVo/AgentOptionVo 数据模型

- [refact] 新增 agent 执行接口的session相关逻辑

- [refact] [local dev] 优化配置管理，环境变量化依赖服务地址，支持多模型配置

- [feat] 新增业务域ID(biz_domain_id)支持，透传到 agent/tool 执行链路
- [feat] 新增对话日志模块(dialog_log_v2)和调试日志管理工具(debug_logs.mk)
- [chore] 更新 dolphinlanguagesdk 依赖到 0.3.3，临时禁用 ContextManager 功能
- [fix] 修复 PyInstaller 打包问题
- [fix] 修复会话初始化时 biz_domain_id 参数未传递的问题
- [feat] 增强 stand_log curl 命令生成：支持单引号转义、gzip 压缩、查询参数 URL 编码
- [feat] 新增 conversation-session/init 请求日志开关配置（log_conversation_session_init）


## 1.2.1
- [refact] Graph RAG 检索客户端优化用户账号header处理

## 1.2.2
- [fix] (api_tool_pkg): 完善v1版本接口中工具参数 schema 类型和描述的处理逻辑，确保存在type和description

## 1.2.3
- [refact] (dip/doc_qa): 密码解码方式从base64改为RSA解密，使用PKCS8格式私钥和PKCS1Padding填充模式
- [refact] (dip/doc_qa): 更新鉴权方式，适配新的安全认证机制

## 1.2.4
- fix: 修复session缓存过期时的NoneType错误
- 新增 exception_logger 模块及相关优化
- fix: 011y SamplerLogger 没有 warning 方法的问题


## 1.2.5
 - [refact] update ignore rule to use standardized way of ignore directories

## 1.2.6
- [refact] Session 模块重构为 Cache 模块，统一命名规范
- [feat] 新增 Agent Cache 管理功能，支持缓存的创建、查询和更新操作
- [fix] 修复 API 工具固定值处理逻辑（process_fixed_value）
- [feat] 新增质量探测 Agent 配置（QualityInsight_Agent）及可观测性数据查询 API 工具箱
- [refact] 移除 `use_context_engineer_v2` 特性开关
- [feat] AgentTool 增加依赖缓存和进度返回支持，新增 `is_skill_agent_need_progress` 配置项
- [fix] 对接DolphinSDK 0.3.7， 解决 explore v1 prompt 模式报错问题

## 1.2.7
- [fix] fix特性标志设置逻辑

## 1.2.8
- [refact] 简化记忆搜索提示词构建逻辑，直接使用 $query 变量进行记忆检索

