# Agent-App 可观测性实现设计

## 1. 概述

本文档详细描述了 Agent-App 可观测性功能的实现设计，包括数据埋点、指标计算、API 接口等核心组件。

## 2. 可观测性埋点设计

### 2.1 埋点时机
Agent 会在每一次 chat 运行完成后（包括成功和失败），借助可观测性日志系统，记录运行结果的各种属性，并生成可观测性日志上报。

### 2.2 埋点数据模型

#### 2.2.1 Run 级别埋点
- **run_id**: 运行唯一标识
- **agent_id**: Agent ID
- **agent_version**: Agent 版本
- **conversation_id**: 对话 ID
- **session_id**: 会话 ID
- **user_id**: 用户 ID
- **call_type**: 调用类型 (chat/debugchat/apichat)
- **start_time**: 开始时间戳
- **end_time**: 结束时间戳
- **ttft**: 首token响应时间 (ms)
- **total_time**: 总执行时间 (ms)
- **total_tokens**: 总token数
- **input_message**: 输入query
- **tool_call_count**: 工具调用次数
- **tool_call_failed_count**: 工具调用失败次数
- **progress**: run运行过程记录，包含以下字段：
  - **id**: 进度ID
  - **agent_name**: Agent名称
  - **stage**: 执行阶段
  - **answer**: 回答内容（可能是工具调用结果）
  - **think**: 思考过程
  - **status**: 状态
  - **skill_info**: 技能信息
    - **type**: 技能类型
    - **name**: 技能名称
    - **args**: 技能参数
    - **checked**: 是否已检查
  - **input_message**: 输入消息
  - **interrupted**: 是否被中断
  - **flags**: 自定义标签
  - **start_time**: 开始时间
  - **end_time**: 结束时间
  - **estimated_input_tokens**: 预估输入token数
  - **estimated_output_tokens**: 预估输出token数
  - **estimated_ratio_tokens**: 预估token比例
  - **token_usage**: token使用情况
    - **prompt_tokens**: 提示token数
    - **completion_tokens**: 完成token数
    - **total_tokens**: 总token数
    - **prompt_tokens_details**: 提示token详情
      - **cached_tokens**: 缓存token数
      - **uncached_tokens**: 非缓存token数
- **status**: 运行状态 (Success/Failed)

## 3. 指标计算体系

索引库存储的是run级别的埋点数据，以下指标从Agent和Session两个维度分别进行计算：

### 3.1 Agent 级别指标

#### 3.1.1 基础指标
- **total_requests**: 总请求数
  - 计算公式：该Agent下所有run记录的数量
  - 计算说明：统计指定时间范围内该Agent产生的所有run记录

- **total_sessions**: 总会话数
  - 计算公式：该Agent下所有唯一session的数量
  - 计算说明：统计指定时间范围内该Agent产生的所有不同session

- **avg_session_rounds**: 平均会话轮次
  - 计算公式：总请求数除以总会话数
  - 计算说明：反映每个会话平均包含的run数量

#### 3.1.2 性能指标
- **run_success_rate**: Run成功率
  - 计算公式：成功run数量除以总run数量，乘以100得到百分比
  - 计算说明：统计状态为"Success"的run占总run的比例

- **avg_execute_duration**: 平均执行时长
  - 计算公式：所有run的总执行时间的平均值  （待确认，是否仅统计成功run）
  - 计算说明：统计该Agent下所有run的total_time字段的平均值

- **avg_ttft_duration**: 平均首token响应时间
  - 计算公式：所有run的首token响应时间的平均值
  - 计算说明：统计该Agent下所有run的ttft字段的平均值

- **tool_success_rate**: 工具调用成功率
  - 计算公式：成功工具调用次数除以总工具调用次数，乘以100得到百分比
  - 计算说明：基于所有run的工具调用失败次数和总调用次数计算

### 3.2 Session 级别指标

- **session_run_count**: Session运行次数
  - 计算公式：该session下所有run记录的数量
  - 计算说明：统计指定session包含的run数量

- **session_duration**: Session时长
  - 计算公式：该session下最后一个run的结束时间减去第一个run的开始时间
  - 计算说明：反映整个session的持续时间

- **avg_run_execute_duration**: 平均运行执行时长
  - 计算公式：该session下所有run的执行时间的平均值
  - 计算说明：统计该session下所有run的total_time字段的平均值

- **avg_run_ttft_duration**: 平均运行首token响应时间
  - 计算公式：该session下所有run的首token响应时间的平均值
  - 计算说明：统计该session下所有run的ttft字段的平均值

- **run_error_count**: 运行错误次数
  - 计算公式：该session下状态为"Failed"的run数量
  - 计算说明：统计该session中失败的run数量

- **tool_fail_count**: 工具失败次数
  - 计算公式：该session下所有run的工具调用失败次数的总和
  - 计算说明：统计该session中所有run的tool_call_failed_count字段的总和

## 4. API 接口设计

### 4.1 Agent 可观测信息查询

#### 接口: `POST /observability/agent/{agent_id}/detail`

**请求参数:**
```json
{
  "agent_version": "string",
  "include_config": false,
  "start_time": 1646360670123,
  "end_time": 1646360670123
}
```

**响应结果:**
```json
{
  "agent": {
    "id": "string",
    "version": "string",
    "key": "string",
    "is_built_in": 0,
    "name": "string",
    "category_id": "string",
    "category_name": "string",
    "profile": "string",
    "config": {},
    "avatar_type": 0,
    "avatar": "string",
    "product_id": 0,
    "product_name": "string",
    "publish_info": {
      "is_api_agent": 0,
      "is_sdk_agent": 0,
      "is_skill_agent": 0,
      "is_data_flow_agent": 0
    }
  },
  "total_requests": 100,
  "total_sessions": 20,
  "avg_session_rounds": 5,
  "run_success_rate": 95.5,
  "avg_execute_duration": 1500,
  "avg_ttft_duration": 200,
  "tool_success_rate": 98.2
}
```

### 4.2 对话列表查询

#### 接口: `POST /observability/agent/{agent_id}/conversation`

**请求参数:**
```json
{
  "agent_version": "string",
  "title": "string",
  "size": 10,
  "page": 1
}
```

**响应结果:**
```json
{
  "entries": [
    {
      "id": "string",
      "title": "string",
      "origin": "string",
      "create_time": 1646360670123,
      "update_time": 1646360670123,
      "status": "completed"
    }
  ],
  "total_count": 100
}
```

### 4.3 Session 列表查询

#### 接口: `POST /observability/agent/{agent_id}/conversation/{conversation_id}/session`

**请求参数:**
```json
{
  "agent_version": "string",
  "start_time": 1646360670123,
  "end_time": 1646360670123,
  "size": 10,
  "page": 1
}
```

**响应结果:**
```json
{
  "entries": [
    {
      "session_id": "string",
      "start_time": 1646360670123,
      "end_time": 1646360670123,
      "session_run_count": 5,
      "session_duration": 15000,
      "avg_run_execute_duration": 3000,
      "avg_run_ttft_duration": 250,
      "run_error_count": 0,
      "tool_fail_count": 1
    }
  ],
  "total_count": 50
}
```

### 4.4 Session 详情查询

#### 接口: `POST /observability/agent/{agent_id}/conversation/{conversation_id}/session/{session_id}/detail`

**请求参数:**
```json
{
  "agent_version": "string",
  "start_time": 1646360670123,
  "end_time": 1646360670123
}
```

**响应结果:**
```json
{
  "session_id": "string",
  "start_time": 1646360670123,
  "end_time": 1646360670123,
  "session_run_count": 5,
  "session_duration": 15000,
  "avg_run_execute_duration": 3000,
  "avg_run_ttft_duration": 250,
  "run_error_count": 0,
  "tool_fail_count": 1
}
```

### 4.5 Run 列表查询

#### 接口: `POST /observability/agent/{agent_id}/conversation/{conversation_id}/session/{session_id}/run`

**请求参数:**
```json
{
  "agent_version": "string",
  "start_time": 1646360670123,
  "end_time": 1646360670123,
  "page": 1,
  "size": 10
}
```

**响应结果:**
```json
{
  "entries": [
    {
      "run_id": "string",
      "agent_id": "string",
      "agent_version": "string",
      "conversation_id": "string",
      "session_id": "string",
      "user_id": "string",
      "call_type": "chat",
      "start_time": 1646360670123,
      "end_time": 1646360670123,
      "ttft": 200,
      "total_time": 3000,
      "total_tokens": 1500,
      "input_message": "用户输入内容",
      "tool_call_count": 3,
      "tool_call_failed_count": 0,
      "progress": [
        {
          "id": "string",
          "agent_name": "string",
          "stage": "string",
          "answer": "string",
          "think": "string",
          "status": "string",
          "skill_info": {
            "type": "string",
            "name": "string",
            "args": [
              {
                "name": "string",
                "value": "string",
                "type": "string"
              }
            ],
            "checked": true
          },
          "input_message": "string",
          "interrupted": false,
          "flags": {},
          "start_time": 1646360670123,
          "end_time": 1646360670123,
          "estimated_input_tokens": 100,
          "estimated_output_tokens": 50,
          "estimated_ratio_tokens": 0.5,
          "token_usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
            "prompt_tokens_details": {
              "cached_tokens": 20,
              "uncached_tokens": 80
            }
          }
        }
      ],
      "status": "Success"
    }
  ],
  "total_count": 5
}
```

### 4.6 Run 详情查询

#### 接口: `POST /observability/agent/{agent_id}/conversation/{conversation_id}/session/{session_id}/run/{run_id}/detail`

**请求参数:**
```json
{
  "agent_version": "string",
  "start_time": 1646360670123,
  "end_time": 1646360670123
}
```

**响应结果:**
```json
{
  "run_id": "string",
  "agent_id": "string",
  "agent_version": "string",
  "conversation_id": "string",
  "session_id": "string",
  "user_id": "string",
  "call_type": "chat",
  "start_time": 1646360670123,
  "end_time": 1646360670123,
  "ttft": 200,
  "total_time": 3000,
  "total_tokens": 1500,
  "input_message": "用户输入内容",
  "tool_call_count": 3,
  "tool_call_failed_count": 0,
  "progress": [
    {
      "id": "string",
      "agent_name": "string",
      "stage": "string",
      "answer": "string",
      "think": "string",
      "status": "string",
      "skill_info": {
        "type": "string",
        "name": "string",
        "args": [
          {
            "name": "string",
            "value": "string",
            "type": "string"
          }
        ],
        "checked": true
      },
      "input_message": "string",
      "interrupted": false,
      "flags": {},
      "start_time": 1646360670123,
      "end_time": 1646360670123,
      "estimated_input_tokens": 100,
      "estimated_output_tokens": 50,
      "estimated_ratio_tokens": 0.5,
      "token_usage": {
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "total_tokens": 150,
        "prompt_tokens_details": {
          "cached_tokens": 20,
          "uncached_tokens": 80
        }
      }
    }
  ],
  "status": "Success"
}
```

## 5. 实现架构

### 5.1 数据流架构

```
Agent 运行 → 埋点数据收集 → 可观测性日志系统 → 数据视图 → API 查询 → 前端展示
```

### 5.2 核心组件

1. **数据收集层**: 负责在 Agent 运行时收集各类指标数据
2. **数据处理层**: 对原始数据进行清洗、聚合、计算
3. **数据存储层**: 存储可观测性数据，支持快速查询
4. **API 服务层**: 提供可观测性数据查询接口
5. **前端展示层**: 可视化展示 Agent 运行状态和性能指标

### 5.3 技术实现

- **数据收集**: 使用结构化日志记录，支持实时流式处理
- **数据存储**: 采用时序数据库存储时间序列数据
- **查询引擎**: 支持复杂聚合查询和时间范围过滤
- **缓存策略**: 对热点数据进行缓存，提升查询性能

## 6. 错误处理与监控

### 6.1 错误处理策略

- **数据完整性**: 确保埋点数据的完整性和一致性
- **异常捕获**: 对数据收集和处理过程中的异常进行捕获和处理
- **降级策略**: 在数据源不可用时提供降级方案

### 6.2 监控指标

- **API 响应时间**: 监控各接口的响应性能
- **数据准确性**: 监控指标计算的准确性
- **系统可用性**: 监控可观测性系统的整体可用性

## 7. 扩展性设计

### 7.1 指标扩展
- 支持自定义指标的定义和计算
- 支持指标维度的灵活扩展

### 7.2 数据源扩展
- 支持多种数据源的接入
- 支持实时和历史数据的混合查询

### 7.3 查询能力扩展
- 支持复杂的多维度聚合查询
- 支持自定义时间窗口的指标计算

## 8. 性能优化

### 8.1 查询优化
- 使用索引优化常用查询路径
- 采用预聚合策略减少实时计算开销

### 8.2 存储优化
- 数据分区存储，按时间范围进行分区
- 冷热数据分离，优化存储成本

### 8.3 缓存策略
- 热点数据缓存，减少数据库查询压力
- 查询结果缓存，提升重复查询性能