# AI Agent Observability & Quality Optimization

## 1. 背景（Background）

随着 AI Agent 在企业内部快速普及，系统对 性能稳定性、质量可控性、成本可控性、用户体验 的要求日益提高。
然而当前 Agent 系统普遍存在：

运行链路不透明（看不到模型执行/工具调用/上下文流转）

无法定位质量问题（错误不知道发生在哪里）

用户体验不可量化（满意度与成功率无法自动评估）

缺乏优化闭环（没有智能优化建议）

### ❌ 1. 可观测能力弱

无法知道 Agent 为什么慢

工具调用链路不可见

错误原因不明确

### ❌ 2. 用户体验无法量化

用户到底满意还是不满意？

多轮对话是否高效？

用户会话为什么突然中断？

### ❌ 3. 质量问题无自动化检测

幻觉识别靠人工

回答逻辑错误无检测

工具参数错误无人警告

### ❌ 4. 缺乏自动优化建议

不知道应该修改 Prompt？

还是应该调整工具？

或者应该增强知识库？

因此需要构建一套统一的 Agent Observability（可观测）与 Quality Insights（质量分析/优化建议） 能力。


## 2. 愿景（Vision）

构建 从上到下清晰、有指标、有链路、有分析、有建议 的 Agent 可观测和质量分析能力，实现：

- ✔ 每一次执行都可以追踪
- ✔ 每一次质量问题都能自动识别
- ✔ 每一次低质量表现都能给出优化建议
- ✔ 每个 Agent 都有可衡量的“健康状态”
- ✔ 每个对话的用户体验可以量化
- ✔ 最终实现自我优化、自我诊断的智能体系统

## 3. 关键目标（Key Goals）
![alt text](image.png)
Agent在运行一段时间后，期望可以结合以下信息对Agent的配置或提示词自动调优，以使Agent达成最好的效果，同时，也可以基于过去一段时间内的Agent运行时进行运维分析与trace链路等分析

整体目标划分为两个主方向：
### 🎯 目标 1：Agent 可观测（Observability）

1. 建立三层级可观测体系
    - Agent
    - Session
    - Run（含 完整 Progress 链路）

2. 对 Agent 多维度监控
    - 请求量
    - 成功率
    - 工具调用情况
    - 时延
    - 错误原因
    - ....

3. 完整链路透明化

可看到：
```
输入 → 模型 → 推理 → 工具 → 再推理 → 最终输出

```

4. 可视化 Dashboard
    - Agent 总览
    - Session 详情
    - Run Trace


### 🎯 目标 2：Agent 质量分析 & 优化建议（Quality Insights）
1. 自动质量检测
    - 逻辑错误
    - 信息不一致
    - 无关回答
    - 工具错误
    - 用户挫败感征兆

2. 用户体验自动评估
    - 用户满意度（显式/隐式）
    - Session 完整性
    - 对话轮数效率

3. 优化建议生成

从以下角度给出 actionable insights：

    - Prompt 提示词优化
    - 工具调用优化
    - 知识库补充建议
    - Agent 任务结构调整


## 4. 核心概念与对象模型（Key Concepts）

需要统一定义四个层级：
```
Agent → Session → Run →  Progress
```
用于从高层聚合 → 低层诊断。

### 4.1 Agent（智能体）

一个 Agent 实例（如客服 Agent、旅行规划 Agent）。

生命周期：长期存在，多个用户共享。

一个 Agent = 多个 Session 的父对象

### 4.2 Session （一次完整对话）

Session 是用户与 Agent 的 完整交互生命周期。

生命周期：从用户发送第一条消息 → 本轮对话结束。

Session 触发条件：

- 用户发送第一条消息（启动）
- 一段时间无活动（自动结束）
- 用户主动结束（如点击“结束对话”）
- 系统判断任务已完成

### 4.3 Run （一次问答）

Run = 用户的一次提问 + Agent 的一次回答,是 Session 最小可观测单元。

每个 Run 可能包含多个 Span（如工具调用）。

### 4.4 Progress（执行链路）
Span 用于描述 Agent 执行链路中的细节步骤，类似 OpenTelemetry。


## 5. 产品能力拆解（Two Core Capabilities）
- 能力 1：**Agent 可观测（Observability）**： 基于 Agent → Session → Run → Progresses 四个层级逐级展开。
- 能力 2：**Agent 质量分析 & 优化建议（Quality Insights）**：对三大维度执行分析 → 生成可执行的优化建议。

## 6. 功能一：Agent 可观测能力设计（核心）

### 6.1 可观测体系结构（Observability Model）
AI Agent Observability 模型包含：

- Metrics（数值指标）
- Traces（链路追踪）
- Logs（文本日志事件）

三者结合构成一个完整可观测系统。

#### 6.1.1 Metrics（指标）

用于统计整体情况，回答：

- 是否变慢？
- 是否成功率下降？
- 工具错误是否增加？

Metrics 按照三层级提供：

- Agent 级指标
- Session 级指标
- Run 级指标

#### 6.1.2 Traces（链路追踪）
Traces 解决：

- Agent 过程是什么？
- 调用了哪些工具？
- 工具失败在哪里？

#### 6.1.3 Logs（事件日志）

记录关键事件：

- tool.failed
- model.failed
- session.ended
- retry.triggered

### 6.2 Metrics（指标）

#### 6.2.1 Agent 级可观测（Global / Aggregated Metrics）

| 指标名称（英文） | 中文名 | 描述 | 单位 | 维度属性 |
|------------------|--------|------|------|----------|
| Total Requests(√) | 总请求数 | Agent 累计处理的用户请求总次数 | 次 | 全局/聚合指标 |
| Unique Users | 独立用户数 | 发起请求的 distinct 用户总数 | 个 | 全局/聚合指标 |
| Total Sessions (√)| 总会话数 | Agent 完成的完整用户会话总次数（通常以用户会话结束或超时界定） | 个 | 全局/聚合指标 |
| Avg Session Rounds  (√) | 平均会话轮次 | 所有会话的平均交互轮数（每轮为一次用户请求+Agent响应） | 轮/会话 | 全局/聚合指标 |
| Run Success Rate  (√)| 任务成功率 | 成功完成 Run 的请求/会话占比（需结合业务场景定义“成功”） | % | 全局/聚合指标 |
| Agent Crash Rate | Agent 崩溃率 | Agent 运行过程中发生崩溃的请求/会话占比 | % | 全局/聚合指标 |
| Avg Execute Duration  (√)| 平均执行耗时 | 分别代表 50%/90%/99% 的请求响应时间处于该数值以下，反映响应速度分布 | ms（毫秒） | 全局/聚合指标 |
| Avg TTFT Duration  (√)| 平均首 Token 响应耗时 | 从用户发起请求到收到 Agent 首次有效响应的平均时间，衡量首屏加载体验 | ms（毫秒） | 全局/聚合指标 |
| Tool Success Rate (√)| 工具成功率 | Agent 调用外部工具时执行成功的请求占比（如工具超时、返回错误结果等） | % | 全局/聚合指标 |
| Cost per Request | 单次请求成本 | 处理单个用户请求的平均资源/资金成本（如算力、API 费用等） | 元（或对应货币单位） | 全局/聚合指标 |
| Cost per Session | 单会话成本 | 处理单个完整会话的平均资源/资金成本（如算力、API 费用等） | 元（或对应货币单位） | 全局/聚合指标 |
| Request Trend (Hourly/Daily) | 请求趋势（小时/天） | 按小时或天维度统计的请求数变化趋势，反映流量波动 | 次/小时 或 次/天 | 趋势指标 |
| Success Rate Trend | 成功率趋势 | 按时间维度（小时/天）统计的任务成功率变化趋势 | %/小时 或 %/天 | 趋势指标 |
| Error Rate Trend | 错误率趋势 | 按时间维度（小时/天）统计的各类错误（含崩溃、工具失败等）占比变化趋势 | %/小时 或 %/天 | 趋势指标 |
| Tool Fail Rate Trend | 工具失败趋势 | 按时间维度（小时/天）统计的工具调用失败率变化趋势 | %/小时 或 %/天 | 趋势指标 |
| Agent Response Time Trend | Agent响应时间趋势 | 按时间维度（小时/天）统计的平均响应时间（或 p50/p90/p99）变化趋势 | ms/小时 或 ms/天 | 趋势指标 |


#### 6.2.2 Session 级可观测（Conversation-level）
| 指标名称（英文） | 中文名 | 描述 | 单位 | 维度属性 |
|------------------|--------|------|------|----------|
| Session Run Count (√)| 会话总轮数 | 单个会话中用户请求与Agent响应的总交互轮次 | 轮 | 会话维度指标 |
| Session Duration (√)| 会话时长 | 从会话启动到结束（或超时）的总时间跨度 | ms（毫秒）/ min（分钟） | 会话维度指标 |
| ⚠️ Session Status | 任务状态 | ⚠️ **注**：Session缺少状态字段，无法直接获取任务完成状态 | 枚举值（Success/Failed/Abandoned/Timeout） | 会话/任务维度指标 |
| Avg Run Execute Duration (√) | 平均执行耗时	 | 单个会话所有 Run 的平均响应耗时（不含分位数，仅平均值） | ms（毫秒） | 全局/会话维度指标 |
| Avg Run TTFT Duration  (√)| 平均首 Token 响应耗时 | 单个会话所有 Run 的首次有效响应的平均时间，衡量首屏加载体验 | ms（毫秒） | 全局/聚合指标 |
| Run Error Count(√) | Run错误次数 | Session 中 Run 失败的总次数 | 次 | 全局/会话维度指标 |
| Tool Fail Count(√) | 工具错误次数 | Agent在会话（或全局）中调用外部工具时发生失败的总次数 | 次 | 全局/会话维度指标 |
| Cost  | 单会话成本 | 处理单个完整会话的总资源/资金成本（单次请求成本×会话总轮数，含固定成本分摊） | 元（或对应货币单位） | 全局/会话维度指标 |
| Cost per Request | 单次请求成本 | 处理单个用户请求的平均资源/资金成本（含模型调用、工具调用、算力等费用） | 元（或对应货币单位） | 全局/请求维度指标 |


#### 6.2.3 Run 级可观测（Execution Unit）

Run 是最细粒度，也是链路追踪的核心。

##### Run 元数据

- Input Message

- Output Message

- Model Used（with tokens）

- Response Time（模型 & 工具）

- Token 输入/输出

- Tools Invoked（按顺序）

##### Progress 结构

每个 Run 包含完整路径：

```
============================================================
    Dolphin Runtime Call Chain - Execution Time: 31.30s    
============================================================
 🤖 Agent[deepsearch]
  ├─ 📦 Block[AssignBlock]
    ├─ ⚡ Progress[6505decc] (1 stages)
      ├─ 🔄 Stage[TypeStage.ASSIGN] - Status.COMPLETED
  ├─ 📦 Block[ExploreBlock]
    ├─ ⚡ Progress[f90992d8] (19 stages)
      ├─ 🔄 Stage[TypeStage.LLM] - Status.COMPLETED
      ├─ 🔄 Stage[TypeStage.SKILL] - Status.PROCESSING
      ├─ 🔄 Stage[TypeStage.LLM] - Status.COMPLETED
============================================================
Total instances: 25
Summary: 1 Agents, 2 Blocks, 2 Progresses, 20 Stages
============================================================
```
详细的链路属性和指标参数当前debug progress 的实现：
![alt text](image-2.png)


## 7. 功能二：Agent 质量分析 & 优化建议（Quality Insights）

### 7.1 总体设计思路

基于 Agent 三层可观测数据（Agent → Session → Run → Progress），构建统一的智能体驱动的自动化质量分析系统。通过一个质量分析Agent，接收分析参数后调用数据查询工具获取可观测数据，然后根据分析类型自动选择对应的分析策略，实现从宏观到微观的质量问题发现、证据引用和优化建议生成。

**核心架构**：
```
┌─────────────────────────────────────────────────────────────┐
│                   统一质量分析Agent架构                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐  │
│  │         质量分析Agent (QualityAnalysisAgent)          │  │
│  │  输入: {analysis_level, id, start_time, end_time}    │  │
│  │  输出: {analysis_result}                              │  │
│  └────────────┬─────────────────────────┬────────────────┘  │
│               │ 1. 调用数据查询工具            │                  │
│               ▼                            │                  │
│      ┌────────▼────────┐                   │                  │
│      │  数据查询工具     │ ◄───────────────────┤                  │
│      │  (OpenAPI 3.0)   │ 2. 返回metrics & config                  │
│      └────────┬────────┘                   │                  │
│               │                            │                  │
│               ▼ 3. 拼接上下文              │                  │
│      ┌────────▼────────┐       ┌────────▼────────┐          │
│      │  Agent级分析策略  │       │  Session级分析策略│          │
│      │  - 聚合分析      │       │  - 对话分析      │          │
│      │  - 趋势检测      │       │  - 模式识别      │          │
│      │  - 配置优化      │       │  - 效率评估      │          │
│      └────────┬────────┘       └────────┬────────┘          │
│               │                         │                  │
│      ┌────────▼────────┐                                         │
│      │  Run级分析策略   │                                         │
│      │  - Progress链路 │                                         │
│      │  - 工具调用分析  │                                         │
│      │  - 质量检测      │                                         │
│      └─────────────────┘                                         │
└─────────────────────────────────────────────────────────────┘
```

**Agent输入参数**：

- `analysis_level`: 分析类型枚举值，取值范围：
    - `"agent"`: Agent级分析
    - `"session"`: Session级分析
    - `"run"`: Run级分析

- `id`: 分析类型的对象id
    - Agent级分析 → Agent ID
    - Session级分析 → Session ID
    - Run级分析 → Run ID

- `start_time`: 分析数据的开始时间（Unix时间戳）

- `end_time`: 分析数据的结束时间（Unix时间戳）

**完整输入示例（Agent级分析）**：
```json
{
  "analysis_level": "agent",
  "id": "agent_123",
  "start_time": 1732032000000,
  "end_time": 1732118400000
}
```

**Agent分析流程**：

1. **参数接收**：Agent接收分析参数（analysis_level, id, start_time, end_time）
2. **调用数据查询工具**：根据参数调用`analytics_query_tool`获取可观测数据
3. **上下文拼接**：将返回的metrics和agent_config数据拼接到提示词中
4. **执行分析**：基于analysis_level选择对应分析策略进行质量分析
5. **返回结果**：输出结构化的分析报告

**分析查询工具接口（OpenAPI 3.0）**：

接口文档地址：http://10.4.111.139:34000/feature-agent-executor-5.2.0/docs/private/agent-app%2Fv1%2Fagent-app#tag/%E5%8F%AF%E8%A7%82%E6%B5%8B%E6%80%A7/paths/~1api~1agent-app~1v1~1observability~1analytics_query/post
```yaml
openapi: 3.0.0
info:
  title: 数据查询工具 API
  description: 查询Agent/Session/Run的可观测数据和配置信息
  version: 1.0.0
paths:
  /analytics/query:
    post:
      summary: 查询可观测数据
      description: 根据分析类型和时间范围查询相应的metrics和配置数据
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AnalyticsQueryRequest'
      responses:
        '200':
          description: 查询成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AnalyticsQueryResponse'
        '400':
          description: 请求参数错误
        '404':
          description: 指定ID的数据不存在
        '500':
          description: 服务器内部错误
components:
  schemas:
    AnalyticsQueryRequest:
      type: object
      required:
        - analysis_level
        - id
        - start_time
        - end_time
      properties:
        analysis_level:
          type: string
          enum: ["agent", "session", "run"]
          description: 分析类型
        id:
          type: string
          description: 分析对象ID（Agent ID / Session ID / Run ID）
        start_time:
          type: integer
          format: int64
          description: 开始时间（Unix时间戳）
        end_time:
          type: integer
          format: int64
          description: 结束时间（Unix时间戳）
    AnalyticsQueryResponse:
      type: object
      required:
        - success
        - data
      properties:
        success:
          type: boolean
          description: 请求是否成功
        data:
          oneOf:
            - $ref: '#/components/schemas/AgentMetrics'
            - $ref: '#/components/schemas/SessionMetrics'
            - $ref: '#/components/schemas/RunMetrics'
          description: 根据analysis_level返回对应的数据
        error:
          type: string
          description: 错误信息（如果有）
    AgentMetrics:
      type: object
      required:
        - agent_config
        - agent_metrics
      properties:
        agent_config:
          type: object
          properties:
            input:
              type: object
              properties:
                fields:
                  type: array
                  items:
                    type: object
                    properties:
                      name:
                        type: string
                      type:
                        type: string
                      desc:
                        type: string
                rewrite:
                  type: object
                  properties:
                    enable:
                      type: boolean
                    llm_config:
                      type: object
                      properties:
                        id:
                          type: string
                        name:
                          type: string
                        model_type:
                          type: string
                        temperature:
                          type: number
                          format: float
                        top_p:
                          type: number
                          format: float
                        top_k:
                          type: integer
                        frequency_penalty:
                          type: number
                          format: float
                        presence_penalty:
                          type: number
                          format: float
                        max_tokens:
                          type: integer
                augment:
                  type: object
                  properties:
                    enable:
                      type: boolean
                    data_source:
                      type: object
                      properties:
                        kg:
                          type: array
                is_temp_zone_enabled:
                  type: integer
                temp_zone_config:
                  type: object
            system_prompt:
              type: string
              description: 系统提示词
            dolphin:
              type: string
              description: Dolphin模式配置
            is_dolphin_mode:
              type: integer
            pre_dolphin:
              type: array
              items:
                type: object
                properties:
                  key:
                    type: string
                  name:
                    type: string
                  value:
                    type: string
                  enabled:
                    type: boolean
                  edited:
                    type: boolean
            post_dolphin:
              type: array
            data_source:
              type: object
              properties:
                kg:
                  type: array
                doc:
                  type: array
                metric:
                  type: array
                kn_entry:
                  type: array
                knowledge_network:
                  type: array
                advanced_config:
                  type: object
                  properties:
                    kg:
                      type: object
                    doc:
                      type: object
            skills:
              type: object
              properties:
                tools:
                  type: array
                  items:
                    type: object
                    properties:
                      tool_id:
                        type: string
                      tool_box_id:
                        type: string
                      tool_timeout:
                        type: integer
                      tool_input:
                        type: array
                        items:
                          type: object
                          properties:
                            input_name:
                              type: string
                            input_type:
                              type: string
                            input_desc:
                              type: string
                            map_type:
                              type: string
                            map_value:
                              type: string
                            enable:
                              type: boolean
                      intervention:
                        type: boolean
                      result_process_strategies:
                        type: object
                agents:
                  type: array
                mcps:
                  type: array
            llms:
              type: array
              items:
                type: object
                properties:
                  is_default:
                    type: boolean
                  llm_config:
                    type: object
                    properties:
                      id:
                        type: string
                      name:
                        type: string
                      model_type:
                        type: string
                      temperature:
                        type: number
                        format: float
                      top_p:
                        type: number
                        format: float
                      top_k:
                        type: integer
                      frequency_penalty:
                        type: number
                        format: float
                      presence_penalty:
                        type: number
                        format: float
                      max_tokens:
                        type: integer
            is_data_flow_set_enabled:
              type: integer
            opening_remark_config:
              type: object
            preset_questions:
              type: array
              items:
                type: object
                properties:
                  question:
                    type: string
            output:
              type: object
              properties:
                variables:
                  type: object
                  properties:
                    answer_var:
                      type: string
                    doc_retrieval_var:
                      type: string
                    graph_retrieval_var:
                      type: string
                    related_questions_var:
                      type: string
                    other_vars:
                      type: object
                    middle_output_vars:
                      type: object
                default_format:
                  type: string
            built_in_can_edit_fields:
              type: object
            memory:
              type: object
              properties:
                is_enabled:
                  type: boolean
            related_question:
              type: object
              properties:
                is_enabled:
                  type: boolean
            plan_mode:
              type: object
            metadata:
              type: object
              properties:
                config_version:
                  type: string
          description: Agent配置信息
        agent_metrics:
          type: object
          properties:
            total_requests:
              type: integer
              description: 总请求数
            total_sessions:
              type: integer
              description: 总会话数
            avg_session_rounds:
              type: integer
              description: 平均会话轮次
            run_success_rate:
              type: number
              format: float
              minimum: 0
              maximum: 1
              description: 任务成功率
            avg_ttft_duration:
              type: number
              format: float
              description: 平均首Token响应耗时（毫秒）
            tool_success_rate:
              type: number
              format: float
              minimum: 0
              maximum: 1
              description: 工具成功率
          description: Agent级指标数据
        session_list:
          type: array
          items:
            type: object
            properties:
              session_id:
                type: string
              session_start_time:
                type: string
                format: date-time
              session_end_time:
                type: string
                format: date-time
              session_duration:
                type: integer
                format: int64
          description: 会话列表
        trend_data:
          type: object
          properties:
            last_7_days:
              type: array
              items:
                type: object
              description: 过去7天趋势数据
            last_24_hours:
              type: array
              items:
                type: object
              description: 过去24小时趋势数据
          description: 趋势数据
    SessionMetrics:
      type: object
      required:
        - session_metrics
        - agent_config
        - run_list
      properties:
        session_metrics:
          type: object
          properties:
            session_run_count:
              type: integer
              description: 会话总轮数
            session_duration:
              type: integer
              format: int64
              description: 会话时长（毫秒）
            avg_run_execute_duration:
              type: number
              format: float
              description: 平均执行耗时（毫秒）
            avg_run_ttft_duration:
              type: number
              format: float
              description: 平均首Token响应耗时（毫秒）
            run_error_count:
              type: integer
              description: Run错误次数
            tool_fail_count:
              type: integer
              description: 工具错误次数
          description: 会话指标数据
        agent_config:
          type: object
          description: Agent配置信息（结构同AgentMetrics中的agent_config）
        run_list:
          type: array
          items:
            type: object
            properties:
              run_id:
                type: string
                description: Run ID
              response_time:
                type: number
                format: float
                description: 响应时间（毫秒）
              status:
                type: string
                description: 状态
          description: Run列表信息
    RunMetrics:
      type: object
      required:
        - run_id
        - input
        - output
        - progress
      properties:
        run_id:
          type: string
          description: Run ID
        input:
          type: string
          description: 输入内容
        output:
          type: string
          description: 输出内容
        start_time:
          type: integer
          format: int64
          description: 开始时间（Unix时间戳）
        end_time:
          type: integer
          format: int64
          description: 结束时间（Unix时间戳）
        token_usage:
          type: integer
          description: Token使用量
        ttft:
          type: number
          format: float
          description: 首Token响应时间（毫秒）
        progress:
          type: array
          items:
            type: object
            properties:
              agent_name:
                type: string
                description: Agent名称
              stage:
                type: string
                description: 阶段
              answer:
                type: string
                description: 回答内容
              think:
                type: string
                description: 思考内容
              status:
                type: string
                description: 执行状态
              skill_info:
                type: object
                description: 技能信息
              block_answer:
                type: string
                description: 块答案
              input_message:
                type: string
                description: 输入消息
              interrupted:
                type: boolean
                description: 是否中断
          description: Progress链路信息
```

### 7.2 数据来源与输入

#### 7.2.1 Agent 级数据源
```json
{
  "agent_metrics": {
    "total_requests": 10000,
    "total_sessions": 100,
    "avg_session_rounds": 1200,
    "run_success_rate": 0.15,
    "avg_ttft_duration": 500,
    "tool_success_rate ": 0.60
  },
  "agent_config": {
        "input": {
            "fields": [
                {
                    "name": "query",
                    "type": "string",
                    "desc": ""
                },
                {
                    "name": "history",
                    "type": "object",
                    "desc": ""
                },
                {
                    "name": "tool",
                    "type": "object",
                    "desc": ""
                },
                {
                    "name": "header",
                    "type": "object",
                    "desc": ""
                },
                {
                    "name": "self_config",
                    "type": "object",
                    "desc": ""
                }
            ],
            "rewrite": {
                "enable": false,
                "llm_config": {
                    "id": "",
                    "name": "test",
                    "model_type": "llm",
                    "temperature": 0.5,
                    "top_p": 0.5,
                    "top_k": 0,
                    "frequency_penalty": 0,
                    "presence_penalty": 0,
                    "max_tokens": 1000
                }
            },
            "augment": {
                "enable": false,
                "data_source": {
                    "kg": []
                }
            },
            "is_temp_zone_enabled": 0,
            "temp_zone_config": null
        },
        "system_prompt": "请调用技能：online_search_cite_tool 回答用户问题：$query ，直接输出answer中的answer值，不要再思考。并且需要保留工具中返回的index信息。",
        "dolphin": "/prompt/输出提示语：正在联网搜索，请稍等...，不要输出其他内容->intro\r\n@online_search_cite_tool(query=$query)->result\r\n$result['answer']['answer'] -> web_content\r\n$result['answer']['references'] -> web_ref\r\n/explore/(history=True)\r\n直接输出$web_content，一定要保留index信息！！！\r\n参考信息是$web_ref。\r\n-> answ",
        "is_dolphin_mode": 1,
        "pre_dolphin": [
            {
                "key": "context_organize",
                "name": "上下文组织模块",
                "value": "\n{\"query\": \"用户的问题为: \"+$query} -> context\n",
                "enabled": true,
                "edited": false
            }
        ],
        "post_dolphin": [],
        "data_source": {
            "kg": [],
            "doc": [],
            "metric": [],
            "kn_entry": [],
            "knowledge_network": [],
            "advanced_config": {
                "kg": null,
                "doc": null
            }
        },
        "skills": {
            "tools": [
                {
                    "tool_id": "80fefb6c-9c94-4661-b9c9-5dba3e0fe726",
                    "tool_box_id": "bf0da1b2-e3b5-4bc5-83a2-ef0d3042ed83",
                    "tool_timeout": 300,
                    "tool_input": [
                        {
                            "input_name": "search_tool",
                            "input_type": "string",
                            "input_desc": "搜索工具",
                            "map_type": "fixedValue",
                            "map_value": "zhipu_search_tool",
                            "enable": true
                        },
                        {
                            "input_name": "stream",
                            "input_type": "boolean",
                            "input_desc": "是否流式返回",
                            "map_type": "fixedValue",
                            "map_value": "true",
                            "enable": true
                        },
                        {
                            "input_name": "token",
                            "input_type": "string",
                            "input_desc": "令牌",
                            "map_type": "var",
                            "map_value": "header.token",
                            "enable": true
                        },
                        {
                            "input_name": "api_key",
                            "input_type": "string",
                            "input_desc": "搜索工具API密钥",
                            "map_type": "fixedValue",
                            "map_value": "1828616286d4c94b26071585e1f93009.negnhMi3D5KVuc7h",
                            "enable": true
                        },
                        {
                            "input_name": "model_name",
                            "input_type": "string",
                            "input_desc": "模型名称",
                            "map_type": "fixedValue",
                            "map_value": "deepseek_v3",
                            "enable": true
                        },
                        {
                            "input_name": "query",
                            "input_type": "string",
                            "input_desc": "搜索查询词",
                            "map_type": "auto",
                            "map_value": "",
                            "enable": true
                        }
                    ],
                    "intervention": false,
                    "result_process_strategies": null
                }
            ],
            "agents": [],
            "mcps": []
        },
        "llms": [
            {
                "is_default": true,
                "llm_config": {
                    "id": "1950850444926521344",
                    "name": "deepseek_v3",
                    "model_type": "llm",
                    "temperature": 1,
                    "top_p": 1,
                    "top_k": 1,
                    "frequency_penalty": 0,
                    "presence_penalty": 0,
                    "max_tokens": 8000
                }
            }
        ],
        "is_data_flow_set_enabled": 0,
        "opening_remark_config": null,
        "preset_questions": [
            {
                "question": "如何学习python"
            }
        ],
        "output": {
            "variables": {
                "answer_var": "answ",
                "doc_retrieval_var": "doc_retrieval_res",
                "graph_retrieval_var": "graph_retrieval_res",
                "related_questions_var": "related_questions",
                "other_vars": null,
                "middle_output_vars": null
            },
            "default_format": "markdown"
        },
        "built_in_can_edit_fields": null,
        "memory": {
            "is_enabled": false
        },
        "related_question": {
            "is_enabled": false
        },
        "plan_mode": null,
        "metadata": {
            "config_version": "v1"
        }
  },
  "session_list": [
    {
      "session_id": "sess_123",
      "session_start_time": "2023-05-01T12:00:00Z",
      "session_end_time": "2023-05-01T13:00:00Z",
      "session_duration": 300000,
    }
  ],
  "trend_data": {
    "last_7_days": [],
    "last_24_hours": []
  } 
}
```

#### 7.2.2 Session 级数据源
```json
{
  "session_metrics": {
    "session_run_count": 10,
    "session_duration": 300000,
    "avg_run_execute_duration": 30000,
    "avg_run_ttft_duration": 500,
    "run_error_count": 100,
    "tool_fail_count": 50,
  },
  "agent_config": {
        "input": {
            "fields": [
                {
                    "name": "query",
                    "type": "string",
                    "desc": ""
                },
                {
                    "name": "history",
                    "type": "object",
                    "desc": ""
                },
                {
                    "name": "tool",
                    "type": "object",
                    "desc": ""
                },
                {
                    "name": "header",
                    "type": "object",
                    "desc": ""
                },
                {
                    "name": "self_config",
                    "type": "object",
                    "desc": ""
                }
            ],
            "rewrite": {
                "enable": false,
                "llm_config": {
                    "id": "",
                    "name": "test",
                    "model_type": "llm",
                    "temperature": 0.5,
                    "top_p": 0.5,
                    "top_k": 0,
                    "frequency_penalty": 0,
                    "presence_penalty": 0,
                    "max_tokens": 1000
                }
            },
            "augment": {
                "enable": false,
                "data_source": {
                    "kg": []
                }
            },
            "is_temp_zone_enabled": 0,
            "temp_zone_config": null
        },
        "system_prompt": "请调用技能：online_search_cite_tool 回答用户问题：$query ，直接输出answer中的answer值，不要再思考。并且需要保留工具中返回的index信息。",
        "dolphin": "/prompt/输出提示语：正在联网搜索，请稍等...，不要输出其他内容->intro\r\n@online_search_cite_tool(query=$query)->result\r\n$result['answer']['answer'] -> web_content\r\n$result['answer']['references'] -> web_ref\r\n/explore/(history=True)\r\n直接输出$web_content，一定要保留index信息！！！\r\n参考信息是$web_ref。\r\n-> answ",
        "is_dolphin_mode": 1,
        "pre_dolphin": [
            {
                "key": "context_organize",
                "name": "上下文组织模块",
                "value": "\n{\"query\": \"用户的问题为: \"+$query} -> context\n",
                "enabled": true,
                "edited": false
            }
        ],
        "post_dolphin": [],
        "data_source": {
            "kg": [],
            "doc": [],
            "metric": [],
            "kn_entry": [],
            "knowledge_network": [],
            "advanced_config": {
                "kg": null,
                "doc": null
            }
        },
        "skills": {
            "tools": [
                {
                    "tool_id": "80fefb6c-9c94-4661-b9c9-5dba3e0fe726",
                    "tool_box_id": "bf0da1b2-e3b5-4bc5-83a2-ef0d3042ed83",
                    "tool_timeout": 300,
                    "tool_input": [
                        {
                            "input_name": "search_tool",
                            "input_type": "string",
                            "input_desc": "搜索工具",
                            "map_type": "fixedValue",
                            "map_value": "zhipu_search_tool",
                            "enable": true
                        },
                        {
                            "input_name": "stream",
                            "input_type": "boolean",
                            "input_desc": "是否流式返回",
                            "map_type": "fixedValue",
                            "map_value": "true",
                            "enable": true
                        },
                        {
                            "input_name": "token",
                            "input_type": "string",
                            "input_desc": "令牌",
                            "map_type": "var",
                            "map_value": "header.token",
                            "enable": true
                        },
                        {
                            "input_name": "api_key",
                            "input_type": "string",
                            "input_desc": "搜索工具API密钥",
                            "map_type": "fixedValue",
                            "map_value": "1828616286d4c94b26071585e1f93009.negnhMi3D5KVuc7h",
                            "enable": true
                        },
                        {
                            "input_name": "model_name",
                            "input_type": "string",
                            "input_desc": "模型名称",
                            "map_type": "fixedValue",
                            "map_value": "deepseek_v3",
                            "enable": true
                        },
                        {
                            "input_name": "query",
                            "input_type": "string",
                            "input_desc": "搜索查询词",
                            "map_type": "auto",
                            "map_value": "",
                            "enable": true
                        }
                    ],
                    "intervention": false,
                    "result_process_strategies": null
                }
            ],
            "agents": [],
            "mcps": []
        },
        "llms": [
            {
                "is_default": true,
                "llm_config": {
                    "id": "1950850444926521344",
                    "name": "deepseek_v3",
                    "model_type": "llm",
                    "temperature": 1,
                    "top_p": 1,
                    "top_k": 1,
                    "frequency_penalty": 0,
                    "presence_penalty": 0,
                    "max_tokens": 8000
                }
            }
        ],
        "is_data_flow_set_enabled": 0,
        "opening_remark_config": null,
        "preset_questions": [
            {
                "question": "如何学习python"
            }
        ],
        "output": {
            "variables": {
                "answer_var": "answ",
                "doc_retrieval_var": "doc_retrieval_res",
                "graph_retrieval_var": "graph_retrieval_res",
                "related_questions_var": "related_questions",
                "other_vars": null,
                "middle_output_vars": null
            },
            "default_format": "markdown"
        },
        "built_in_can_edit_fields": null,
        "memory": {
            "is_enabled": false
        },
        "related_question": {
            "is_enabled": false
        },
        "plan_mode": null,
        "metadata": {
            "config_version": "v1"
        }
  },
  "run_list": [
    { "run_id": "run_1", "response_time": 75000, "status": "success" },
    { "run_id": "run_2", "response_time": 75000, "status": "success" },
    { "run_id": "run_3", "response_time": 75000, "status": "success" },
  ]
}
```

#### 7.2.3 Run 级数据源
```json
{
  "run_id": "run_789",
  "input": "用户问题",
  "output": "Agent回答",
  "start_time": 1680000000000,
  "end_time": 1680000100000,
  "token_usage": 100000,
  "ttft": 300,
  "progress": [
    {
      "agent_name": "main",
      "stage": "llm", 
      "answer": "你好！很高兴见到你！我是ABC，一个AI助手。有什么我可以帮你的吗？😊",
      "think": "",
      "status": "completed",
      "skill_info": null,
      "block_answer": "",
      "input_message": "你好啊",
      "interrupted": false
    }
  ]
  
}
```
### 7.3 统一质量分析Agent设计

#### 7.3.1 Agent输入定义

质量分析Agent接收结构化的输入参数，用于执行不同级别的质量分析。

### 全局输入参数

| 参数名 | 类型 | 必填 | 取值范围 | 说明 |
|--------|------|------|----------|------|
| `data_source` | Object | ✅ 是 | - | 数据源对象，结构根据analysis_level变化 |
| `analysis_level` | String | ✅ 是 | `"agent"` / `"session"` / `"run"` | 分析类型枚举值，决定数据源结构和分析策略 |

---

### 按分析级别的数据源参数详细说明

#### 1️⃣ Agent级分析（analysis_level="agent"）

**分析目标**：宏观系统健康度评估，识别系统性问题和优化方向

**数据源结构**：

| 参数名 | 类型 | 必填 | 数据结构 | 说明 |
|--------|------|------|----------|------|
| `agent_metrics` | Object | ✅ 是 | 聚合指标对象 | Agent级性能指标数据 |
| `agent_config` | Object | ✅ 是 | 完整配置对象 | Agent的完整配置信息（包含input、system_prompt、skills等） |
| `session_list` | Array | ❌ 否 | Session对象数组 | 历史会话列表（用于趋势分析） |
| `trend_data` | Object | ❌ 否 | 趋势数据对象 | 24小时/7天趋势数据（用于异常检测） |

**详细字段说明**：

| 字段路径 | 类型 | 说明 | 示例 |
|----------|------|------|------|
| `agent_metrics.total_requests` | Integer | 总请求数 | 10000 |
| `agent_metrics.total_sessions` | Integer | 总会话数 | 100 |
| `agent_metrics.avg_session_rounds` | Integer | 平均会话轮次 | 12 |
| `agent_metrics.run_success_rate` | Float | 任务成功率（0-1） | 0.85 |
| `agent_metrics.avg_ttft_duration` | Float | 平均首Token响应耗时（毫秒） | 500 |
| `agent_metrics.tool_success_rate` | Float | 工具成功率（0-1） | 0.90 |
| `agent_config.input.fields[]` | Array | 输入字段配置 | [{"name": "query", "type": "string"}] |
| `agent_config.system_prompt` | String | 系统提示词 | "请调用技能回答用户问题..." |
| `agent_config.skills.tools[]` | Array | 工具配置数组 | 包含工具ID、参数映射等 |
| `agent_config.llms[]` | Array | 模型配置数组 | 包含模型ID、温度参数等 |
| `session_list[].session_id` | String | 会话ID | "sess_123" |
| `session_list[].session_duration` | Integer | 会话时长（毫秒） | 300000 |
| `trend_data.last_24_hours[]` | Array | 24小时趋势数据 | 时间序列数据点 |

---

#### 2️⃣ Session级分析（analysis_level="session"）

**分析目标**：单次会话的完整流程分析，识别对话质量和用户体验问题

**数据源结构**：

| 参数名 | 类型 | 必填 | 数据结构 | 说明 |
|--------|------|------|----------|------|
| `session_metrics` | Object | ✅ 是 | 会话指标对象 | 单个Session的性能和质量指标 |
| `agent_config` | Object | ✅ 是 | 完整配置对象 | 当时使用的Agent配置信息 |
| `run_list` | Array | ✅ 是 | Run对象数组 | 该会话中所有Run的详细信息 |

**详细字段说明**：

| 字段路径 | 类型 | 说明 | 示例 |
|----------|------|------|------|
| `session_metrics.session_run_count` | Integer | 会话总轮数 | 15 |
| `session_metrics.session_duration` | Integer | 会话时长（毫秒） | 300000 |
| `session_metrics.avg_run_execute_duration` | Float | 平均执行耗时（毫秒） | 30000 |
| `session_metrics.avg_run_ttft_duration` | Float | 平均首Token响应耗时（毫秒） | 500 |
| `session_metrics.run_error_count` | Integer | Run错误次数 | 2 |
| `session_metrics.tool_fail_count` | Integer | 工具错误次数 | 1 |
| `run_list[].run_id` | String | Run ID | "run_1" |
| `run_list[].response_time` | Float | 响应时间（毫秒） | 75000 |
| `run_list[].status` | String | 状态 | "success" / "failed" |
| `agent_config.input` | Object | 输入配置 | 同Agent级结构 |
| `agent_config.system_prompt` | String | 系统提示词 | 同Agent级结构 |
| `agent_config.skills` | Object | 技能配置 | 同Agent级结构 |

---

#### 3️⃣ Run级分析（analysis_level="run"）

**分析目标**：深度分析单次执行的每个Progress，识别具体质量和技术瓶颈

**数据源结构**：

| 参数名 | 类型 | 必填 | 数据结构 | 说明 |
|--------|------|------|----------|------|
| `run_id` | String | ✅ 是 | 基本信息 | 单次执行的唯一标识符 |
| `input` | String | ✅ 是 | 基本信息 | 用户输入内容 |
| `output` | String | ✅ 是 | 基本信息 | Agent输出内容 |
| `start_time` | Integer | ✅ 是 | 时间指标 | 开始时间（Unix时间戳） |
| `end_time` | Integer | ✅ 是 | 时间指标 | 结束时间（Unix时间戳） |
| `token_usage` | Integer | ✅ 是 | 性能指标 | Token使用量 |
| `ttft` | Float | ✅ 是 | 性能指标 | 首Token响应时间（毫秒） |
| `progress` | Array | ✅ 是 | Progress对象数组 | 详细的执行链路信息 |

**详细字段说明**：

| 字段路径 | 类型 | 说明 | 示例 |
|----------|------|------|------|
| `run_id` | String | Run唯一标识符 | "run_789" |
| `input` | String | 用户输入内容 | "请分析2024年Q1的销售额趋势" |
| `output` | String | Agent输出内容 | "根据数据分析，2024年Q1销售额..." |
| `start_time` | Integer | 开始时间戳（毫秒） | 1680000000000 |
| `end_time` | Integer | 结束时间戳（毫秒） | 1680000100000 |
| `token_usage` | Integer | Token使用总量 | 100000 |
| `ttft` | Float | 首Token响应时间（毫秒） | 300 |
| `progress[].agent_name` | String | Agent名称 | "main" |
| `progress[].stage` | String | 执行阶段 | "llm" / "TOOL_CALL" |
| `progress[].answer` | String | 阶段输出内容 | "我将帮您分析..." |
| `progress[].status` | String | 执行状态 | "completed" / "failed" |
| `progress[].skill_info` | Object | 工具调用信息 | 工具名、参数、结果等 |
| `progress[].interrupted` | Boolean | 是否中断 | false |

---

### 输入参数验证规则

| 验证规则 | 说明 | 错误示例 |
|----------|------|----------|
| `analysis_level`必须为枚举值 | 取值只能是"agent"、"session"、"run" | "invalid_level" |
| `data_source`结构必须匹配`analysis_level` | 不同级别的数据源结构不同 | Agent级缺少agent_metrics字段 |
| 必填字段不能为空 | ✅标记的字段不能缺失或为null | agent_metrics为null |
| 时间戳必须为有效Unix时间 | start_time和end_time必须为正整数 | "2023-05-01"（字符串格式） |
| Progress数组不能为空 | Run级progress数组至少包含一个Stage | progress: [] |

**完整输入示例（Agent级）**：

```json
{
  "data_source": {
    "agent_metrics": {
      "total_requests": 10000,
      "total_sessions": 100,
      "avg_session_rounds": 1200,
      "run_success_rate": 0.15,
      "avg_ttft_duration": 500,
      "tool_success_rate": 0.60
    },
    "agent_config": {
      "input": {
        "fields": [
          {"name": "query", "type": "string", "desc": ""},
          {"name": "history", "type": "object", "desc": ""},
          {"name": "tool", "type": "object", "desc": ""},
          {"name": "header", "type": "object", "desc": ""},
          {"name": "self_config", "type": "object", "desc": ""}
        ],
        "rewrite": {
          "enable": false,
          "llm_config": {
            "id": "",
            "name": "test",
            "model_type": "llm",
            "temperature": 0.5,
            "top_p": 0.5,
            "top_k": 0,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "max_tokens": 1000
          }
        },
        "augment": {
          "enable": false,
          "data_source": {"kg": []}
        },
        "is_temp_zone_enabled": 0,
        "temp_zone_config": null
      },
      "system_prompt": "请调用技能：online_search_cite_tool 回答用户问题...",
      "dolphin": "/prompt/输出提示语：正在联网搜索，请稍等...",
      "is_dolphin_mode": 1,
      "pre_dolphin": [
        {
          "key": "context_organize",
          "name": "上下文组织模块",
          "value": "\n{\"query\": \"用户的问题为: \"+$query} -> context\n",
          "enabled": true,
          "edited": false
        }
      ],
      "post_dolphin": [],
      "data_source": {
        "kg": [],
        "doc": [],
        "metric": [],
        "kn_entry": [],
        "knowledge_network": [],
        "advanced_config": {"kg": null, "doc": null}
      },
      "skills": {
        "tools": [
          {
            "tool_id": "80fefb6c-9c94-4661-b9c9-5dba3e0fe726",
            "tool_box_id": "bf0da1b2-e3b5-4bc5-83a2-ef0d3042ed83",
            "tool_timeout": 300,
            "tool_input": [
              {
                "input_name": "search_tool",
                "input_type": "string",
                "input_desc": "搜索工具",
                "map_type": "fixedValue",
                "map_value": "zhipu_search_tool",
                "enable": true
              },
              {
                "input_name": "stream",
                "input_type": "boolean",
                "input_desc": "是否流式返回",
                "map_type": "fixedValue",
                "map_value": "true",
                "enable": true
              },
              {
                "input_name": "token",
                "input_type": "string",
                "input_desc": "令牌",
                "map_type": "var",
                "map_value": "header.token",
                "enable": true
              },
              {
                "input_name": "api_key",
                "input_type": "string",
                "input_desc": "搜索工具API密钥",
                "map_type": "fixedValue",
                "map_value": "1828616286d4c94b26071585e1f93009.negnhMi3D5KVuc7h",
                "enable": true
              },
              {
                "input_name": "model_name",
                "input_type": "string",
                "input_desc": "模型名称",
                "map_type": "fixedValue",
                "map_value": "deepseek_v3",
                "enable": true
              },
              {
                "input_name": "query",
                "input_type": "string",
                "input_desc": "搜索查询词",
                "map_type": "auto",
                "map_value": "",
                "enable": true
              }
            ],
            "intervention": false,
            "result_process_strategies": null
          }
        ],
        "agents": [],
        "mcps": []
      },
      "llms": [
        {
          "is_default": true,
          "llm_config": {
            "id": "1950850444926521344",
            "name": "deepseek_v3",
            "model_type": "llm",
            "temperature": 1,
            "top_p": 1,
            "top_k": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "max_tokens": 8000
          }
        }
      ],
      "is_data_flow_set_enabled": 0,
      "opening_remark_config": null,
      "preset_questions": [{"question": "如何学习python"}],
      "output": {
        "variables": {
          "answer_var": "answ",
          "doc_retrieval_var": "doc_retrieval_res",
          "graph_retrieval_var": "graph_retrieval_res",
          "related_questions_var": "related_questions",
          "other_vars": null,
          "middle_output_vars": null
        },
        "default_format": "markdown"
      },
      "built_in_can_edit_fields": null,
      "memory": {"is_enabled": false},
      "related_question": {"is_enabled": false},
      "plan_mode": null,
      "metadata": {"config_version": "v1"}
    },
    "session_list": [
      {
        "session_id": "sess_123",
        "session_start_time": "2023-05-01T12:00:00Z",
        "session_end_time": "2023-05-01T13:00:00Z",
        "session_duration": 300000
      }
    ],
    "trend_data": {
      "last_7_days": [],
      "last_24_hours": []
    }
  },
  "analysis_level": "agent"
}
```

**Session级完整输入示例**：

```json
{
  "data_source": {
    "session_metrics": {
      "session_run_count": 10,
      "session_duration": 300000,
      "avg_run_execute_duration": 30000,
      "avg_run_ttft_duration": 500,
      "run_error_count": 100,
      "tool_fail_count": 50
    },
    "agent_config": {
      "input": {
        "fields": [
          {"name": "query", "type": "string", "desc": ""},
          {"name": "history", "type": "object", "desc": ""},
          {"name": "tool", "type": "object", "desc": ""},
          {"name": "header", "type": "object", "desc": ""},
          {"name": "self_config", "type": "object", "desc": ""}
        ],
        "rewrite": {
          "enable": false,
          "llm_config": {
            "id": "",
            "name": "test",
            "model_type": "llm",
            "temperature": 0.5,
            "top_p": 0.5,
            "top_k": 0,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "max_tokens": 1000
          }
        },
        "augment": {
          "enable": false,
          "data_source": {"kg": []}
        },
        "is_temp_zone_enabled": 0,
        "temp_zone_config": null
      },
      "system_prompt": "请调用技能：online_search_cite_tool 回答用户问题...",
      "dolphin": "/prompt/输出提示语：正在联网搜索，请稍等...",
      "is_dolphin_mode": 1,
      "pre_dolphin": [
        {
          "key": "context_organize",
          "name": "上下文组织模块",
          "value": "\n{\"query\": \"用户的问题为: \"+$query} -> context\n",
          "enabled": true,
          "edited": false
        }
      ],
      "post_dolphin": [],
      "data_source": {
        "kg": [],
        "doc": [],
        "metric": [],
        "kn_entry": [],
        "knowledge_network": [],
        "advanced_config": {"kg": null, "doc": null}
      },
      "skills": {
        "tools": [
          {
            "tool_id": "80fefb6c-9c94-4661-b9c9-5dba3e0fe726",
            "tool_box_id": "bf0da1b2-e3b5-4bc5-83a2-ef0d3042ed83",
            "tool_timeout": 300,
            "tool_input": [
              {
                "input_name": "search_tool",
                "input_type": "string",
                "input_desc": "搜索工具",
                "map_type": "fixedValue",
                "map_value": "zhipu_search_tool",
                "enable": true
              },
              {
                "input_name": "stream",
                "input_type": "boolean",
                "input_desc": "是否流式返回",
                "map_type": "fixedValue",
                "map_value": "true",
                "enable": true
              },
              {
                "input_name": "token",
                "input_type": "string",
                "input_desc": "令牌",
                "map_type": "var",
                "map_value": "header.token",
                "enable": true
              },
              {
                "input_name": "api_key",
                "input_type": "string",
                "input_desc": "搜索工具API密钥",
                "map_type": "fixedValue",
                "map_value": "1828616286d4c94b26071585e1f93009.negnhMi3D5KVuc7h",
                "enable": true
              },
              {
                "input_name": "model_name",
                "input_type": "string",
                "input_desc": "模型名称",
                "map_type": "fixedValue",
                "map_value": "deepseek_v3",
                "enable": true
              },
              {
                "input_name": "query",
                "input_type": "string",
                "input_desc": "搜索查询词",
                "map_type": "auto",
                "map_value": "",
                "enable": true
              }
            ],
            "intervention": false,
            "result_process_strategies": null
          }
        ],
        "agents": [],
        "mcps": []
      },
      "llms": [
        {
          "is_default": true,
          "llm_config": {
            "id": "1950850444926521344",
            "name": "deepseek_v3",
            "model_type": "llm",
            "temperature": 1,
            "top_p": 1,
            "top_k": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "max_tokens": 8000
          }
        }
      ],
      "is_data_flow_set_enabled": 0,
      "opening_remark_config": null,
      "preset_questions": [{"question": "如何学习python"}],
      "output": {
        "variables": {
          "answer_var": "answ",
          "doc_retrieval_var": "doc_retrieval_res",
          "graph_retrieval_var": "graph_retrieval_res",
          "related_questions_var": "related_questions",
          "other_vars": null,
          "middle_output_vars": null
        },
        "default_format": "markdown"
      },
      "built_in_can_edit_fields": null,
      "memory": {"is_enabled": false},
      "related_question": {"is_enabled": false},
      "plan_mode": null,
      "metadata": {"config_version": "v1"}
    },
    "run_list": [
      {"run_id": "run_1", "response_time": 75000, "status": "success"},
      {"run_id": "run_2", "response_time": 75000, "status": "success"},
      {"run_id": "run_3", "response_time": 75000, "status": "success"}
    ]
  },
  "analysis_level": "session"
}
```

**Run级完整输入示例**：

```json
{
  "data_source": {
    "run_id": "run_789",
    "input": "用户问题",
    "output": "Agent回答",
    "start_time": 1680000000000,
    "end_time": 1680000100000,
    "token_usage": 100000,
    "ttft": 300,
    "progress": [
      {
        "agent_name": "main",
        "stage": "llm",
        "answer": "你好！很高兴见到你！我是ABC，一个AI助手。有什么我可以帮你的吗？😊",
        "think": "",
        "status": "completed",
        "skill_info": null,
        "block_answer": "",
        "input_message": "你好啊",
        "interrupted": false
      }
    ]
  },
  "analysis_level": "run"
}
```

#### 7.3.2 统一返回结果定义

所有层级的分析均返回一致结构的结果：

```json
{
  "analysis_metadata": {
    "analysis_level": "agent|session|run",
    "target_id": "agent_123|sess_789|run_456",
    "timestamp": "2025-11-19T10:30:00Z",
    "data_period": "2025-11-19 00:00:00 - 2025-11-19 23:59:59"
  },
  "summary": "Agent整体运行正常，但存在响应延迟偏高问题",
  "scores": {
    "overall": 75,
    "dimensions": {
      "stability": 85,
      "performance": 72,
      "quality": 80,
      "efficiency": 68
    }
  },
  "findings": [
    {
      "category": "performance|quality|efficiency|stability",
      "issue_id": "HIGH_LATENCY",
      "severity": "critical|high|medium|low",
      "description": "问题描述",
      "evidence": [
        "P95响应时间: 2500ms",
        "超过阈值: 2000ms"
      ],
      "impact": "影响范围和程度描述",
      "recommendations": [
        {
          "action": "具体行动",
          "details": "详细说明",
          "expected_impact": "预期收益",
          "priority": 1
        }
      ]
    }
  ],
  "confidence": 0.85
}
```

**参数说明**：

**为什么三层级分析使用一致结构？**

统一返回结构的核心目的是**实现跨层级的无缝切换和关联分析**。无论分析的是Agent整体、单个Session还是具体Run，调用方都能以相同的方式解析和处理结果，大大降低了系统复杂度。

**详细字段说明**：

| 字段路径 | 类型 | 说明 | 适用层级 |
|---------|------|------|----------|
| **analysis_metadata** | Object | 分析元数据，包含分析的基本信息 | 所有层级 |
| analysis_metadata.analysis_level | String | 分析类型：<br/>- `"agent"`: Agent级宏观分析<br/>- `"session"`: Session级对话分析<br/>- `"run"`: Run级精细分析 | 所有层级 |
| analysis_metadata.target_id | String | 被分析对象的唯一标识符：<br/>- Agent级：`agent_123`（Agent ID）<br/>- Session级：`sess_789`（Session ID）<br/>- Run级：`run_456`（Run ID） | 所有层级 |
| analysis_metadata.timestamp | String | 分析执行的时间戳（ISO 8601格式），如"2025-11-19T10:30:00Z" | 所有层级 |
| analysis_metadata.data_period | String | 分析使用的数据时间范围，格式："YYYY-MM-DD HH\:mm:ss - YYYY-MM-DD HH\:mm:ss"<br/>例："2025-11-19 00:00:00 - 2025-11-19 23:59:59" | 所有层级 |
| **summary** | String | 分析总结摘要（50字以内），简洁描述整体健康状态和主要问题 | 所有层级 |
| **scores** | Object | 质量评分体系，提供可量化的健康度指标 | 所有层级 |
| scores.overall | Integer | 整体评分（0-100），基于四个维度的加权平均 | 所有层级 |
| scores.dimensions | Object | 四个维度的细分评分（0-100） | 所有层级 |
| scores.dimensions.stability | Integer | **稳定性评分**：衡量系统运行的稳定性和可靠性<br/>- Agent级：成功率、崩溃率、错误率趋势<br/>- Session级：对话完整性、中断率<br/>- Run级：执行成功率、异常率 | 所有层级 |
| scores.dimensions.performance | Integer | **性能评分**：衡量响应速度和资源利用效率<br/>- Agent级：平均响应时间、吞吐量<br/>- Session级：会话时长、轮次效率<br/>- Run级：执行延迟、TTFT | 所有层级 |
| scores.dimensions.quality | Integer | **质量评分**：衡量输出质量和准确性<br/>- Agent级：用户满意度、反馈质量<br/>- Session级：回答准确性、上下文一致性<br/>- Run级：答案正确性、相关性 | 所有层级 |
| scores.dimensions.efficiency | Integer | **效率评分**：衡量资源使用和成本效益<br/>- Agent级：成本效益比、资源利用率<br/>- Session级：任务完成效率<br/>- Run级：Token效率、工具调用效率 | 所有层级 |
| **findings** | Array | 问题发现列表，每个元素代表一个识别出的问题 | 所有层级 |
| findings[].category | String | 问题分类，取值：<br/>- `"performance"`: 性能问题（延迟、吞吐量）<br/>- `"quality"`: 质量问题（准确性、一致性）<br/>- `"efficiency"`: 效率问题（成本、资源浪费）<br/>- `"stability"`: 稳定性问题（崩溃、错误） | 所有层级 |
| findings[].issue_id | String | 问题唯一标识符，采用`UPPER_SNAKE_CASE`命名<br/>例：`HIGH_LATENCY`、`LOW_SUCCESS_RATE`、`REDUNDANT_SEARCH` | 所有层级 |
| findings[].severity | String | 严重程度级别：<br/>- `"critical"`: 严重（影响核心功能，需立即处理）<br/>- `"high"`: 高（影响用户体验，建议优先处理）<br/>- `"medium"`: 中（影响效率，可计划处理）<br/>- `"low"`: 低（优化项，可后续处理） | 所有层级 |
| findings[].description | String | 问题描述，说明具体是什么问题（100字以内） | 所有层级 |
| findings[].evidence | Array | 支撑证据列表，每个元素为字符串，用具体数据证明问题存在<br/>例：`["P95响应时间: 2500ms", "超过阈值: 2000ms"]` | 所有层级 |
| findings[].impact | String | 影响分析，说明问题对系统、用户或业务的影响范围和程度 | 所有层级 |
| findings[].recommendations | Array | 优化建议列表，提供可执行的改进方案 | 所有层级 |
| recommendations[].action | String | 行动建议，简洁描述需要做什么（20字以内）<br/>例："启用Response Streaming" | 所有层级 |
| recommendations[].details | String | 详细说明，具体如何实施该建议（100字以内）<br/>例："在API响应中启用流式传输，降低用户感知延迟" | 所有层级 |
| recommendations[].expected_impact | String | 预期收益，说明实施建议后能带来的改善<br/>例："降低用户感知延迟50%" | 所有层级 |
| recommendations[].priority | Integer | 建议优先级（1-5），1为最高优先级<br/>优先级基于：严重程度、实现难度、预期收益综合评估 | 所有层级 |
| **confidence** | Float | 分析置信度（0.0-1.0），表示分析结果的可信程度<br/>计算基于：数据完整性(30%) + 证据充分性(25%) + 异常值检测(20%) + 历史一致性(15%) + 逻辑一致性(10%) | 所有层级 |

**统一结构的设计优势**：

1. **解析一致性**：调用方无需根据分析级别编写不同的解析逻辑
2. **可视化友好**：Dashboard可以统一渲染所有层级的分析结果
3. **存储标准化**：分析结果可统一存储在数据库中，便于查询和对比
5. **关联分析**：支持跨层级分析结果关联，如"某个Run的问题如何在Agent级体现"


#### 7.3.3 三层级分析策略

质量分析Agent基于7.2章节提供的数据源，针对三个不同分析级别采用差异化的分析策略。每个级别的分析深度、数据粒度和输出重点都不同，但均遵循"数据驱动、证据充分、建议可执行"的原则。

---

### Agent级分析策略

**目标**：从宏观角度分析Agent整体表现，识别系统性问题和优化方向

**分析范围**：覆盖过去24小时/7天内所有Session和Run的数据

**数据源**：

- `agent_metrics`: 全局聚合指标（total_requests、run_success_rate等）
- `agent_config`: Agent配置信息（模型、工具、提示词等）
- `session_list`: 历史会话列表
- `trend_data`: 趋势数据（24小时/7天维度）

**核心算法**：

1. ~~**趋势异常检测**~~
   - ~~时间序列分析：识别成功率、响应时间的异常波动~~
   - ~~对比分析：当前周期 vs 历史同期数据~~
   - ~~阈值判断：偏离历史均值±2σ触发预警~~

2. **系统性瓶颈定位**
   - 慢请求聚类：基于TTFT和总延迟分布，识别异常长尾
   - 工具稳定性评估：统计各工具失败率和平均耗时
   - 用户满意度分析：基于显式/隐式反馈计算满意度

3. **配置优化建议**
   - 模型配置分析：温度、top_p等参数对结果质量的影响
   - 工具调用优化：识别低效或不必要的工具调用
   - 提示词诊断：通过success_rate对比提示词效果

**评分算法**：

基于7.2章节实际可用的数据字段进行评分计算：

- **stability（稳定性）**: 0.6×`run_success_rate` + 0.4×`tool_success_rate`
  - 基于任务成功率和工具成功率评估系统稳定性
  - 取值范围：0-100分

- **performance（性能）**: 100 - min(100, (`avg_ttft_duration`/1000) × 20)
  - 基于平均首Token响应时间评估性能
  - TTFT < 500ms 得满分，TTFT > 5000ms 得0分
  - 取值范围：0-100分

- **quality（质量）**: 基础评分基于 `run_success_rate`，满分100分
  - ⚠️ **数据限制**：当前数据缺少用户满意度、答案质量等质量指标
  - 建议补充：`user_satisfaction`、`answer_accuracy_rate`、`hallucination_rate`等指标
  - 当前仅能基于成功率间接评估质量

- **efficiency（效率）**: 基于 `avg_session_rounds` 计算会话轮次效率
  - 轮次越少效率越高，基准为5轮/会话
  - 算法：max(0, 100 - (avg_session_rounds - 5) × 10)
  - ⚠️ **数据限制**：缺少成本效率指标，建议补充：`cost_per_request`、`resource_utilization`

**当前数据覆盖度分析**：

- ✅ **稳定性和性能**：数据充足，可准确计算
- ⚠️ **质量指标**：缺少直接质量数据，仅能间接评估
- ⚠️ **效率指标**：缺少成本相关数据，建议补充成本监控

**典型问题类型**：

基于实际可用数据的可检测问题类型：

| 问题类型 | issue_id | 触发条件 | 严重程度判断 | 检测依据 |
|---------|----------|----------|-------------|----------|
| TTFT过长 | HIGH_TTFT | avg_ttft_duration > 1000ms | critical: >3000ms, high: >2000ms, medium: >1000ms | avg_ttft_duration |
| 低成功率 | LOW_SUCCESS_RATE | run_success_rate < 0.7 | critical: <0.5, high: <0.6, medium: <0.7 | run_success_rate |
| 工具不稳定 | TOOL_INSTABILITY | tool_success_rate < 0.8 | critical: <0.5, high: <0.65, medium: <0.8 | tool_success_rate |
| 轮次过多 | TOO_MANY_ROUNDS | avg_session_rounds > 10 | critical: >20, high: >15, medium: >10 | avg_session_rounds |
| 请求量异常 | UNUSUAL_REQUEST_VOLUME | 基于历史趋势的偏离 | critical: 偏离>80%, high: 偏离>50%, medium: 偏离>30% | total_requests + trend_data |
| 会话效率低 | INEFFICIENT_SESSIONS | avg_session_rounds > 基准值2倍 | critical: >4倍, high: >3倍, medium: >2倍 | avg_session_rounds |

**⚠️ 数据限制说明**：

以下问题类型因缺少关键观测数据，**暂无法自动检测**：

| 无法检测的问题 | 缺少的关键数据 | 建议补充的观测指标 |
|--------------|---------------|-------------------|
| 用户满意度低 | user_satisfaction | 用户评分、点赞/点踩数 |
| 答案质量问题 | answer_accuracy_rate | 事实核验准确率、幻觉检测率 |
| 成本过高 | cost_per_request, cost_per_session | 单次请求成本、会话总成本 |
| 资源利用率异常 | resource_utilization | CPU、内存、带宽使用率 |
| 性能趋势异常 | trend_stability | 历史性能基线、异常检测算法 |

**建议**：为了实现完整的问题检测，建议在Agent运行环境中补充成本监控、资源监控和用户反馈收集模块。

**输出重点**：宏观优化建议、系统性改进方案、资源配置调整

**示例发现**：
```json
{
  "category": "performance",
  "issue_id": "HIGH_TTFT",
  "severity": "medium",
  "description": "Agent平均首Token响应时间1200ms，超出推荐阈值",
  "evidence": [
    "avg_ttft_duration: 1200ms",
    "超过推荐阈值: 1000ms",
    "性能评分: 76/100"
  ],
  "impact": "影响所有用户，增加感知延迟，降低用户体验",
  "recommendations": [
    {
      "action": "启用Response Streaming",
      "details": "在API响应中启用流式传输，降低用户感知延迟",
      "expected_impact": "降低用户感知延迟50%",
      "priority": 1
    },
    {
      "action": "优化模型推理速度",
      "details": "考虑切换至推理速度更快的模型或优化prompt长度",
      "expected_impact": "减少TTFT 30-40%",
      "priority": 2
    }
  ]
}
```

**新增示例 - 工具不稳定问题**：
```json
{
  "category": "stability",
  "issue_id": "TOOL_INSTABILITY",
  "severity": "high",
  "description": "工具成功率仅为60%，低于健康阈值",
  "evidence": [
    "tool_success_rate: 0.60",
    "低于健康阈值: 0.80",
    "稳定性评分: 60/100"
  ],
  "impact": "影响40%的工具调用，可能导致任务失败",
  "recommendations": [
    {
      "action": "优化工具容错机制",
      "details": "增加工具调用重试逻辑、超时处理和降级方案",
      "expected_impact": "提升工具成功率至85%以上",
      "priority": 1
    },
    {
      "action": "检查工具输入参数",
      "details": "验证工具参数映射是否正确，减少参数错误导致的失败",
      "expected_impact": "减少20%的工具失败",
      "priority": 2
    }
  ]
}
```

---

### Session级分析策略

**目标**：分析单次会话的完整流程，识别对话质量和用户体验问题

**分析范围**：单个Session的完整对话历史（所有Run序列）

**数据源**：

- `session_metrics`: 会话指标（run_count、duration、error_count等）
- `agent_config`: 当时使用的Agent配置
- `run_list`: 该会话中所有Run的简要信息

**核心算法**：

1. **对话流畅性分析**
   - 轮次合理性评估：实际轮次 vs 期望轮次（基于任务复杂度）
   - 冗余对话检测：识别用户重问、澄清、纠正等低效交互
   - 上下文一致性：检查前后回答是否有逻辑矛盾

2. **用户体验评估**
   - 完成度判断：基于用户行为判断任务是否成功完成
   - 挫败感识别：重试次数增加、对话突然中断、早期退出等信号
   - 效率评分：完成相同目标所需轮次的行业对比

3. **问题定位**
   - 错误点定位：追踪到具体哪个Run、哪个工具调用出现了问题
   - 中断原因分析：用户主动 vs 系统异常 vs 超时
   - 提示词效果评估：基于同类型任务的成功率对比

**评分算法**：

基于7.2章节实际可用数据字段进行评分计算：

- **stability（稳定性）**: 100 - ((run_error_count + tool_fail_count) / max(1, session_run_count) × 100)
  - 基于会话中的错误率评估稳定性
  - 错误率越低稳定性越高
  - ⚠️ **数据限制**：无法获取会话完成状态，仅基于错误率评估
  - 取值范围：0-100分

- **performance（性能）**:
  - 50% × 基于 `avg_run_execute_duration` 的性能评分
  - 30% × 基于 `avg_run_ttft_duration` 的性能评分
  - 20% × 基于 `session_duration` 的合理性评分
  - 执行时间 < 30s 得满分，> 300s 得0分
  - 取值范围：0-100分

- **quality（质量）**: 基础评分基于 `run_error_count`
  - ⚠️ **数据限制**：缺少回答一致性、用户满意度等质量指标
  - 建议补充：`answer_consistency`、`user_satisfaction`、`goal_achievement`等指标
  - 当前仅能基于错误率间接评估质量

- **efficiency（效率）**:
  - 70% × 基于 `session_run_count` 的轮次效率
  - 基准值：5轮/会话，效率 = max(0, 100 - (轮次-5)×10)
  - 30% × 基于 `session_duration` 的时间效率
  - ⚠️ **数据限制**：缺少成本效率指标，建议补充：会话成本、Token效率等

**典型问题类型**：

| 问题类型 | issue_id | 触发条件 | 严重程度判断 |
|---------|----------|----------|-------------|
| 轮次过多 | TOO_MANY_ROUNDS | 轮次 > 平均值2倍 | critical: >3倍, high: >2.5倍, medium: >2倍 |
| 对话中断 | SESSION_INTERRUPTED | 非正常结束 | critical: 系统异常, high: 用户主动退出, medium: 超时 |
| 重复提问 | REPETITIVE_QUESTIONS | 用户重问 > 3次 | critical: >5次, high: >4次, medium: >3次 |
| 回答不一致 | INCONSISTENT_ANSWERS | 前后矛盾 | critical: 关键信息矛盾, high: 一般矛盾, medium: 细节矛盾 |
| 工具失败 | TOOL_FAILURE | 工具调用失败 | critical: 核心工具失败, high: 辅助工具失败, medium: 重试成功 |

**输出重点**：用户体验优化、对话流程改进、具体轮次优化建议

**示例发现**：
```json
{
  "category": "efficiency",
  "issue_id": "TOO_MANY_ROUNDS",
  "severity": "medium",
  "description": "完成简单任务使用了15轮对话",
  "evidence": [
    "平均会话轮次: 8轮",
    "本次会话轮次: 15轮",
    "用户重问次数: 4次"
  ],
  "impact": "用户需要更多交互时间，降低体验效率",
  "recommendations": [
    {
      "action": "优化Agent提示词",
      "details": "在提示词中增加'首次回答需全面具体'的要求",
      "expected_impact": "预计减少30%对话轮次",
      "priority": 1
    }
  ]
}
```

---

### Run级分析策略

**目标**：深度分析单次执行的每个Progress，识别具体的质量问题和技术瓶颈

**分析范围**：单个Run的完整执行链路（所有Progress）

**数据源**：

- `run_id`、`input`、`output`：基本信息
- `start_time`、`end_time`、`token_usage`、`ttft`：性能指标
- `progress`：详细的执行链路（每个Stage的输入、输出、耗时、状态）

**核心算法**：

1. **执行链路分析**
   - Stage耗时分解：识别最耗时的Stage（LLM推理、工具调用等）
   - 并行度分析：检查是否可以并行执行的Stage被串行执行
   - 重试检测：识别因失败而重试的Stage及其原因

2. **输出质量评估**
   - 相关性检查：输出与输入问题的匹配度
   - 完整性评估：是否完整回答了问题的所有子项
   - 事实核验：与知识库对比验证事实准确性（可结合工具返回结果）

3. **工具调用诊断**
   - 调用必要性：是否必须调用该工具才能完成任务
   - 参数正确性：工具输入参数是否符合规范
   - 结果有效性：工具返回结果是否被正确使用

**评分算法**：

基于7.2章节实际可用数据字段进行评分计算：

- **stability（稳定性）**: 基于 `progress` 数组中的状态统计
  - 0.5 × 成功Stage数/总Stage数
  - 0.3 × (1 - 失败Stage数/总Stage数)
  - 0.2 × 重试Stage占比惩罚：max(0, 1 - 重试Stage数/总Stage数)
  - 取值范围：0-100分

- **performance（性能）**:
  - 40% × 基于 `ttft` 的性能评分：100 - min(100, (ttft/1000) × 25)
  - 30% × 基于总执行时间的性能评分：(end_time - start_time)/1000
  - 30% × 基于 `token_usage` 的Token效率评分
  - 取值范围：0-100分

- **quality（质量）**: ⚠️ **数据限制**
  - 缺少 `output_relevance`、`output_completeness`、`fact_accuracy` 等质量指标
  - 当前可基于 `progress` 中的Stage执行情况间接评估
  - 建议补充：答案质量评估、事实核验、用户反馈等指标

- **efficiency（效率）**:
  - 50% × 基于 `token_usage` 的Token效率：期望值 = min(1000, input_length×1.5)
  - 30% × 基于工具调用数量的效率：工具调用越少效率越高
  - 20% × 基于执行链路的效率：总耗时/理想耗时（需估算）
  - ⚠️ **数据限制**：缺少 `tool_efficiency`、`resource_utilization` 等指标

**典型问题类型**：

| 问题类型 | issue_id | 触发条件 | 严重程度判断 |
|---------|----------|----------|-------------|
| 冗余搜索 | REDUNDANT_SEARCH | 相同查询重复 > 2次 | critical: >5次, high: >3次, medium: >2次 |
| 幻觉输出 | HALLUCINATION | 事实错误 | critical: 关键事实错误, high: 一般错误, medium: 细节错误 |
| TTFT过长 | HIGH_TTFT | 首Token响应 > 3s | critical: >5s, high: >4s, medium: >3s |
| 工具超时 | TOOL_TIMEOUT | 工具调用超时 | critical: 核心工具超时, high: 辅助工具超时, medium: 重试成功 |
| Token浪费 | TOKEN_WASTE | Token使用 > 期望值2倍 | critical: >3倍, high: >2.5倍, medium: >2倍 |

**输出重点**：具体执行优化、技术细节改进、工具配置调整

**示例发现**：
```json
{
  "category": "tool_usage",
  "issue_id": "REDUNDANT_SEARCH",
  "severity": "medium",
  "description": "同一查询重复执行3次",
  "evidence": [
    {
      "progress_id": "p_3",
      "stage": "TOOL_CALL",
      "tool": "web_search",
      "query": "数据分析方法",
      "duration": 500,
      "result": "无结果"
    },
    {
      "progress_id": "p_5",
      "stage": "TOOL_CALL",
      "tool": "web_search",
      "query": "数据分析方法",
      "duration": 480,
      "result": "无结果"
    }
  ],
  "impact": "浪费计算资源，增加响应时间",
  "recommendations": [
    {
      "action": "增加搜索结果缓存",
      "details": "对相同查询的结果缓存30分钟",
      "expected_impact": "减少60%重复搜索",
      "priority": 1
    }
  ]
}
```

### 数据覆盖度总结

根据7.2章节提供的数据格式，对三层级分析的完整度进行评估：

#### ✅ 数据充足，可准确计算（绿色）

**Agent级**：

- 稳定性：`run_success_rate`、`tool_success_rate` 充足
- 性能：`avg_ttft_duration` 充足，可准确评估TTFT性能
- 效率：`avg_session_rounds` 充足，可评估对话轮次效率

**Session级**：

- 稳定性：`run_error_count`、`tool_fail_count` 充足
- 性能：`avg_run_execute_duration`、`avg_run_ttft_duration`、`session_duration` 充足
- 效率：`session_run_count`、`session_duration` 充足

**Run级**：

- 稳定性：`progress` 数组中的Stage状态信息充足
- 性能：`start_time`、`end_time`、`ttft`、`token_usage` 充足
- 效率：`token_usage`、`progress` 中的工具调用信息充足

#### ⚠️ 数据缺失，建议补充（黄色）

**Agent级缺失数据**：

- 用户满意度指标：`user_satisfaction`
- 答案质量指标：`answer_accuracy_rate`、`hallucination_rate`
- 成本指标：`cost_per_request`、`cost_per_session`
- 资源利用率：`resource_utilization`（CPU、内存、带宽）
- 历史趋势稳定性：`trend_stability`

**Session级缺失数据**：

- 中断率：`interruption_rate`（需明确中断类型）
- 回答一致性：`answer_consistency`
- 目标达成度：`goal_achievement`
- 成本效率：`session_cost`、`cost_per_run`

**Run级缺失数据**：

- 输出质量：`output_relevance`、`output_completeness`、`fact_accuracy`
- 工具效率：`tool_efficiency`（调用必要性、参数正确性）
- 重试统计：`retry_rate`（需从Progress中提取）
- Stage成功率：`stage_success_rate`（需从Progress中统计）

#### 📋 数据采集建议

为了实现完整的质量分析系统，建议在Agent运行环境中补充以下观测数据：

1. **用户反馈数据**
   - 显式反馈：点赞/点踩、评分、文字评价
   - 隐式反馈：重试次数、会话时长、退出率

2. **成本监控数据**
   - 模型调用成本（Token消耗 × 单价）
   - 工具调用成本（API费用）
   - 基础设施成本（计算、存储、网络）

3. **资源监控数据**
   - CPU使用率、内存使用率
   - 带宽使用情况
   - 存储I/O统计

4. **质量评估数据**
   - 事实核验结果（通过工具返回验证）
   - 回答相关性评分
   - 上下文一致性检查结果

**注意**：当前版本的质量分析Agent已基于可用数据进行了算法优化，可实现80%的问题检测能力。剩余20%的检测能力需要补充上述数据后即可实现。

---

### 三层级分析的关联性

质量分析Agent支持跨层级问题关联分析：

1. **向上关联**：Run级问题 → Session级影响 → Agent级趋势
   - 某Run的工具失败率异常 → 某个Session失败 → Agent整体成功率下降

2. **向下追溯**：Agent级问题 → Session级表现 → Run级根因
   - Agent响应慢 → 某Session轮次多 → Run中TTFT过长

3. **横向对比**：同级别多实例对比
   - Agent级：对比多个Agent的性能差异
   - Session级：对比同类型会话的质量差异
   - Run级：对比同类型Run的执行效率差异

这种关联分析能力使质量分析Agent能够提供"端到端"的问题溯源和优化建议。

### 7.4 Agent Prompt 工程

#### 7.4.1 统一Prompt模板

质量分析Agent的核心是其Prompt设计。Prompt模板采用**自适应结构**，根据`analysis_level`动态调整分析重点和输出内容，确保在不同分析级别下都能提供准确、深入的分析结果。

**模板设计原则**：

1. **角色定位清晰**：明确Agent的专业身份和分析能力边界
2. **分层分析引导**：针对不同分析级别提供差异化的分析策略
3. **数据驱动**：强调基于输入数据进行分析，避免主观臆断
4. **结构化输出**：严格的JSON格式约束，确保输出可解析
5. **可执行建议**：每个建议都必须包含具体行动、详细说明和预期收益

**完整Prompt模板**：

```python
QUALITY_ANALYZER_PROMPT = """
# 角色定义
你是一个专业的AI Agent质量分析专家，拥有丰富的分布式系统、性能优化和用户体验评估经验。你的核心能力是：
- 基于可观测数据分析AI Agent的性能、质量和效率问题
- 识别系统瓶颈并提供可执行的优化建议
- 生成结构化的质量评估报告

## 输入数据
data_source = {data_source_json}
analysis_level = "{analysis_level}"

## 分析级别定义
{analysis_level_description}

## 分析策略指南
根据analysis_level执行以下分析步骤：

### Agent级分析（analysis_level="agent"）
**目标**：宏观系统健康度评估
**分析重点**：
1. 趋势分析：对比历史数据，识别异常波动
   - 成功率趋势：run_success_rate变化
   - 响应时间趋势：P50/P90/P99延迟变化
   - 用户满意度趋势：user_satisfaction变化
2. 瓶颈定位：识别系统级性能瓶颈
   - 工具稳定性：tool_success_rate分析
   - TTFT性能：avg_ttft_duration分析
   - 吞吐量：total_requests vs 资源消耗
3. 配置诊断：分析Agent配置对性能的影响
   - 模型选择：llm_config中的temperature、top_p等参数
   - 工具配置：skills中的tool_input映射
   - 提示词效果：system_prompt和dolphin模式评估

**评分权重**：
- stability: 0.4×成功率 + 0.4×(1-错误率) + 0.2×趋势稳定性
- performance: 0.5×延迟得分 + 0.3×吞吐量得分 + 0.2×TTFT得分
- quality: 0.6×用户满意度 + 0.4×答案质量得分
- efficiency: 0.5×成本效率 + 0.5×资源利用率

### Session级分析（analysis_level="session"）
**目标**：对话流程质量和用户体验评估
**分析重点**：
1. 流畅性分析：评估对话效率
   - 轮次合理性：session_run_count vs 任务复杂度
   - 冗余交互检测：用户重问次数、澄清次数
   - 上下文一致性：前后回答的逻辑连贯性
2. 完成度评估：判断任务是否成功完成
   - ⚠️ **数据限制**：Session缺少完成状态字段，无法直接判断任务完成情况
   - 错误点定位：run_error_count、tool_fail_count分析
   - 中断原因：区分用户主动、系统异常、超时
3. 用户体验：识别挫败感信号
   - 对话时长：session_duration vs 期望时长
   - 满意度：avg_run_ttft_duration对体验的影响

**评分权重**：
- stability: 0.7×(1-错误率) + 0.3×无错轮次比例
- performance: 0.4×效率得分 + 0.3×时长合理性 + 0.3×轮次效率
- quality: 0.5×回答一致性 + 0.3×用户满意度 + 0.2×目标达成
- efficiency: 0.6×轮次效率 + 0.4×时间效率

### Run级分析（analysis_level="run"）
**目标**：单次执行的技术细节和输出质量评估
**分析重点**：
1. 执行链路分析：深度剖析progress中的每个Stage
   - 耗时分解：识别最耗时的Stage（LLM推理/工具调用）
   - 并行度检查：是否存在可并行但串行执行的Stage
   - 重试检测：失败的Stage及其重试原因
2. 输出质量评估：验证回答的准确性和相关性
   - 相关性：input与output的匹配度
   - 完整性：是否完整回答所有子问题
   - 事实准确性：结合progress中的工具结果验证事实
3. 工具调用诊断：评估工具使用的合理性
   - 调用必要性：是否必须调用该工具
   - 参数正确性：tool_input是否符合工具规范
   - 结果有效性：工具返回结果是否被正确使用

**评分权重**：
- stability: 0.4×执行成功 + 0.3×(1-重试率) + 0.3×Stage成功率
- performance: 0.4×延迟 + 0.3×TTFT + 0.3×Token效率
- quality: 0.4×输出相关性 + 0.3×输出完整性 + 0.3×事实准确性
- efficiency: 0.5×Token效率 + 0.3×工具效率 + 0.2×资源利用率

## 分析要求
1. **数据驱动**：所有结论必须基于data_source中的具体数据
2. **量化证据**：每个问题都需要提供具体的数值证据
3. **建议可执行**：推荐方案必须包含：
   - action: 简明行动描述（≤20字）
   - details: 详细实施方案（≤100字）
   - expected_impact: 预期改善效果
   - priority: 优先级（1-5，1最高）
4. **严重程度排序**：按critical > high > medium > low排序
5. **置信度评估**：根据数据完整性、证据充分性评估置信度

## 问题类型参考
- performance: HIGH_LATENCY, LOW_THROUGHPUT, HIGH_TTFT
- stability: LOW_SUCCESS_RATE, TOOL_INSTABILITY, SESSION_INTERRUPTED
- quality: HALLUCINATION, INCONSISTENT_ANSWERS, LOW_SATISFACTION
- efficiency: TOO_MANY_ROUNDS, REDUNDANT_SEARCH, TOKEN_WASTE, HIGH_COST

## 返回格式（严格JSON）
{{
  "analysis_metadata": {{
    "analysis_level": "{analysis_level}",
    "target_id": "根据data_source中的ID字段提取",
    "timestamp": "当前ISO 8601时间戳",
    "data_period": "数据时间范围（如果有start_time和end_time）"
  }},
  "summary": "分析总结（≤50字）",
  "scores": {{
    "overall": 总体评分(0-100),
    "dimensions": {{
      "stability": 稳定性评分(0-100),
      "performance": 性能评分(0-100),
      "quality": 质量评分(0-100),
      "efficiency": 效率评分(0-100)
    }}
  }},
  "findings": [
    {{
      "category": "performance|quality|efficiency|stability",
      "issue_id": "UPPER_SNAKE_CASE唯一标识",
      "severity": "critical|high|medium|low",
      "description": "问题描述（≤100字）",
      "evidence": ["证据1: 具体数值", "证据2: 对比数据"],
      "impact": "影响分析（≤80字）",
      "recommendations": [
        {{
          "action": "行动建议（≤20字）",
          "details": "详细说明（≤100字）",
          "expected_impact": "预期收益（≤50字）",
          "priority": 1-5
        }}
      ]
    }}
  ],
  "confidence": 置信度(0.0-1.0)
}}

## 开始分析
请基于以上指导和输入的data_source，执行{analysis_level}级别的质量分析，输出结构化JSON结果。
"""
```

**Prompt模板的特点**：

1. **自适应分析策略**：根据`analysis_level`提供不同的分析重点和评分权重
2. **详细的算法指导**：给出具体的计算公式和阈值判断标准
3. **问题类型库**：预定义了常见问题类型的issue_id，便于规范化输出
4. **严格格式约束**：明确每个字段的长度限制和取值范围
5. **置信度计算依据**：给出了影响置信度的关键因子

**实际使用示例**（Python代码中填充模板）：

```python
def build_analysis_prompt(data_source, analysis_level):
    description = get_analysis_level_description(analysis_level)
    return QUALITY_ANALYZER_PROMPT.format(
        data_source_json=json.dumps(data_source, ensure_ascii=False, indent=2),
        analysis_level=analysis_level,
        analysis_level_description=description
    )

# 调用质量分析
prompt = build_analysis_prompt(data_source, "agent")
response = llm.invoke(prompt)
result = parse_analysis_result(response.content)
```

### 7.5 使用示例

本章节提供三个完整的使用示例，演示如何调用质量分析Agent进行不同级别的分析。所有示例均严格遵循7.2章节的数据源格式。

---

#### 7.5.1 Agent级分析调用

**场景**：分析某个Agent过去24小时的整体表现，识别系统性问题和优化方向

```python
from quality_analyzer import QualityAnalyzer

# 初始化质量分析器
analyzer = QualityAnalyzer()

# 准备Agent级分析输入（严格遵循7.2.1格式）
agent_input = {
    "data_source": {
        "agent_metrics": {
            "total_requests": 10000,
            "total_sessions": 100,
            "avg_session_rounds": 1200,
            "run_success_rate": 0.15,
            "avg_ttft_duration": 500,
            "tool_success_rate": 0.60
        },
        "agent_config": {
            "input": {
                "fields": [
                    {"name": "query", "type": "string", "desc": ""},
                    {"name": "history", "type": "object", "desc": ""},
                    {"name": "tool", "type": "object", "desc": ""},
                    {"name": "header", "type": "object", "desc": ""},
                    {"name": "self_config", "type": "object", "desc": ""}
                ],
                "rewrite": {
                    "enable": False,
                    "llm_config": {
                        "id": "",
                        "name": "test",
                        "model_type": "llm",
                        "temperature": 0.5,
                        "top_p": 0.5,
                        "top_k": 0,
                        "frequency_penalty": 0,
                        "presence_penalty": 0,
                        "max_tokens": 1000
                    }
                },
                "augment": {
                    "enable": False,
                    "data_source": {"kg": []}
                },
                "is_temp_zone_enabled": 0,
                "temp_zone_config": None
            },
            "system_prompt": "请调用技能：online_search_cite_tool 回答用户问题...",
            "dolphin": "/prompt/输出提示语：正在联网搜索，请稍等...",
            "is_dolphin_mode": 1,
            "pre_dolphin": [
                {
                    "key": "context_organize",
                    "name": "上下文组织模块",
                    "value": "\n{\"query\": \"用户的问题为: \"+$query} -> context\n",
                    "enabled": True,
                    "edited": False
                }
            ],
            "post_dolphin": [],
            "data_source": {
                "kg": [],
                "doc": [],
                "metric": [],
                "kn_entry": [],
                "knowledge_network": [],
                "advanced_config": {"kg": None, "doc": None}
            },
            "skills": {
                "tools": [
                    {
                        "tool_id": "80fefb6c-9c94-4661-b9c9-5dba3e0fe726",
                        "tool_box_id": "bf0da1b2-e3b5-4bc5-83a2-ef0d3042ed83",
                        "tool_timeout": 300,
                        "tool_input": [
                            {
                                "input_name": "search_tool",
                                "input_type": "string",
                                "input_desc": "搜索工具",
                                "map_type": "fixedValue",
                                "map_value": "zhipu_search_tool",
                                "enable": True
                            },
                            {
                                "input_name": "stream",
                                "input_type": "boolean",
                                "input_desc": "是否流式返回",
                                "map_type": "fixedValue",
                                "map_value": "true",
                                "enable": True
                            },
                            {
                                "input_name": "token",
                                "input_type": "string",
                                "input_desc": "令牌",
                                "map_type": "var",
                                "map_value": "header.token",
                                "enable": True
                            },
                            {
                                "input_name": "api_key",
                                "input_type": "string",
                                "input_desc": "搜索工具API密钥",
                                "map_type": "fixedValue",
                                "map_value": "1828616286d4c94b26071585e1f93009.negnhMi3D5KVuc7h",
                                "enable": True
                            },
                            {
                                "input_name": "model_name",
                                "input_type": "string",
                                "input_desc": "模型名称",
                                "map_type": "fixedValue",
                                "map_value": "deepseek_v3",
                                "enable": True
                            },
                            {
                                "input_name": "query",
                                "input_type": "string",
                                "input_desc": "搜索查询词",
                                "map_type": "auto",
                                "map_value": "",
                                "enable": True
                            }
                        ],
                        "intervention": False,
                        "result_process_strategies": None
                    }
                ],
                "agents": [],
                "mcps": []
            },
            "llms": [
                {
                    "is_default": True,
                    "llm_config": {
                        "id": "1950850444926521344",
                        "name": "deepseek_v3",
                        "model_type": "llm",
                        "temperature": 1,
                        "top_p": 1,
                        "top_k": 1,
                        "frequency_penalty": 0,
                        "presence_penalty": 0,
                        "max_tokens": 8000
                    }
                }
            ],
            "is_data_flow_set_enabled": 0,
            "opening_remark_config": None,
            "preset_questions": [{"question": "如何学习python"}],
            "output": {
                "variables": {
                    "answer_var": "answ",
                    "doc_retrieval_var": "doc_retrieval_res",
                    "graph_retrieval_var": "graph_retrieval_res",
                    "related_questions_var": "related_questions",
                    "other_vars": None,
                    "middle_output_vars": None
                },
                "default_format": "markdown"
            },
            "built_in_can_edit_fields": None,
            "memory": {"is_enabled": False},
            "related_question": {"is_enabled": False},
            "plan_mode": None,
            "metadata": {"config_version": "v1"}
        },
        "session_list": [
            {
                "session_id": "sess_123",
                "session_start_time": "2023-05-01T12:00:00Z",
                "session_end_time": "2023-05-01T13:00:00Z",
                "session_duration": 300000
            }
        ],
        "trend_data": {
            "last_7_days": [],
            "last_24_hours": []
        }
    },
    "analysis_level": "agent"
}

# 执行Agent级分析（同步调用）
print("开始Agent级质量分析...")
result = analyzer.analyze(agent_input)

# 处理分析结果
print(f"分析完成时间: {result['analysis_metadata']['timestamp']}")
print(f"整体评分: {result['scores']['overall']}/100")
print(f"稳定性: {result['scores']['dimensions']['stability']}/100")
print(f"性能: {result['scores']['dimensions']['performance']}/100")
print(f"质量: {result['scores']['dimensions']['quality']}/100")
print(f"效率: {result['scores']['dimensions']['efficiency']}/100")
print(f"分析置信度: {result['confidence']:.2f}")

print("\n发现的问题:")
for finding in result['findings']:
    print(f"- [{finding['severity']}] {finding['issue_id']}: {finding['description']}")
    print(f"  影响: {finding['impact']}")
    print(f"  建议: {finding['recommendations'][0]['action']}")

# 异步调用示例（适用于大型Agent分析）
# result = await analyzer.analyze_async(agent_input)
```

**输出示例**：
```json
{
  "analysis_metadata": {
    "analysis_level": "agent",
    "target_id": "agent_123",
    "timestamp": "2025-11-21T10:30:00Z",
    "data_period": "2025-11-20 00:00:00 - 2025-11-21 23:59:59"
  },
  "summary": "Agent整体表现良好，但响应延迟偏高，建议启用Streaming",
  "scores": {
    "overall": 72,
    "dimensions": {
      "stability": 85,
      "performance": 65,
      "quality": 78,
      "efficiency": 70
    }
  },
  "findings": [
    {
      "category": "performance",
      "issue_id": "HIGH_LATENCY",
      "severity": "medium",
      "description": "P95响应时间达2.5秒，超出推荐阈值",
      "evidence": ["P95响应时间: 2500ms", "P99响应时间: 4500ms", "工具调用平均耗时: 600ms"],
      "impact": "影响所有用户，预计降低15%用户满意度",
      "recommendations": [
        {
          "action": "启用Response Streaming",
          "details": "在API响应中启用流式传输，降低用户感知延迟",
          "expected_impact": "降低用户感知延迟50%",
          "priority": 1
        }
      ]
    }
  ],
  "confidence": 0.85
}
```

---

#### 7.5.2 Session级分析调用

**场景**：分析某次用户对话会话的质量和用户体验，识别对话流程问题

```python
# 准备Session级分析输入（严格遵循7.2.2格式）
session_input = {
    "data_source": {
        "session_metrics": {
            "session_run_count": 15,
            "session_duration": 300000,
            "avg_run_execute_duration": 30000,
            "avg_run_ttft_duration": 500,
            "run_error_count": 2,
            "tool_fail_count": 1
        },
        "agent_config": {
            # 与Agent级相同的完整配置（省略重复部分）
            "input": {...},
            "system_prompt": "...",
            "dolphin": "...",
            # ... 其他字段
        },
        "run_list": [
            {"run_id": "run_1", "response_time": 75000, "status": "success"},
            {"run_id": "run_2", "response_time": 75000, "status": "success"},
            {"run_id": "run_3", "response_time": 120000, "status": "failed"},
            {"run_id": "run_4", "response_time": 60000, "status": "success"},
            {"run_id": "run_5", "response_time": 90000, "status": "success"}
        ]
    },
    "analysis_level": "session"
}

# 执行Session级分析
print("开始Session级质量分析...")
result = analyzer.analyze(session_input)

print(f"\n会话 {result['analysis_metadata']['target_id']} 分析结果:")
print(f"分析总结: {result['summary']}")
print(f"整体评分: {result['scores']['overall']}/100")

# 定位问题轮次
for finding in result['findings']:
    if finding['category'] == 'efficiency':
        print(f"\n效率问题: {finding['description']}")
        print("证据:")
        for evidence in finding['evidence']:
            print(f"  - {evidence}")
        print(f"优化建议: {finding['recommendations'][0]['action']}")
```

---

#### 7.5.3 Run级分析调用

**场景**：深度分析某个具体Run的执行过程，识别技术细节问题

```python
# 准备Run级分析输入（严格遵循7.2.3格式）
run_input = {
    "data_source": {
        "run_id": "run_789",
        "input": "请分析2024年Q1的销售额趋势",
        "output": "根据提供的数据，2024年Q1销售额呈现上升趋势...",
        "start_time": 1680000000000,
        "end_time": 1680000100000,
        "token_usage": 100000,
        "ttft": 300,
        "progress": [
            {
                "agent_name": "main",
                "stage": "llm",
                "answer": "我将帮您分析2024年Q1的销售额趋势。",
                "think": "",
                "status": "completed",
                "skill_info": None,
                "block_answer": "",
                "input_message": "请分析2024年Q1的销售额趋势",
                "interrupted": False
            },
            {
                "agent_name": "main",
                "stage": "TOOL_CALL",
                "answer": "",
                "think": "",
                "status": "completed",
                "skill_info": {
                    "tool_name": "data_analysis_tool",
                    "input_params": {"query": "2024 Q1 sales data"},
                    "output": {"trend": "increasing", "growth_rate": "15%"}
                },
                "block_answer": "",
                "input_message": "查询2024年Q1销售数据",
                "interrupted": False
            },
            {
                "agent_name": "main",
                "stage": "llm",
                "answer": "根据数据分析，2024年Q1销售额相比去年同期增长15%...",
                "think": "",
                "status": "completed",
                "skill_info": None,
                "block_answer": "",
                "input_message": "请基于数据分析结果生成回答",
                "interrupted": False
            }
        ]
    },
    "analysis_level": "run"
}

# 执行Run级分析
print("开始Run级质量分析...")
result = analyzer.analyze(run_input)

print(f"\nRun {result['analysis_metadata']['target_id']} 分析结果:")
print(f"执行质量: {result['summary']}")
print(f"Token使用效率: {result['scores']['dimensions']['efficiency']}/100")

# 输出技术问题
for finding in result['findings']:
    print(f"\n技术问题 [{finding['severity']}]:")
    print(f"  类型: {finding['category']}")
    print(f"  描述: {finding['description']}")
    print("  证据:")
    for evidence in finding['evidence']:
        if isinstance(evidence, dict):
            print(f"    - Stage {evidence.get('stage', 'N/A')}: {evidence}")
        else:
            print(f"    - {evidence}")
```

---

#### 批量分析示例

```python
# 批量分析多个Session
session_ids = ["sess_001", "sess_002", "sess_003"]
batch_results = []

for session_id in session_ids:
    # 获取Session数据（从数据库或API）
    session_data = get_session_data(session_id)

    # 执行分析
    result = analyzer.analyze({
        "data_source": session_data,
        "analysis_level": "session"
    })

    batch_results.append({
        "session_id": session_id,
        "score": result['scores']['overall'],
        "findings_count": len(result['findings']),
        "confidence": result['confidence']
    })

# 生成批量分析报告
print("批量分析报告:")
for item in batch_results:
    print(f"- Session {item['session_id']}: 评分{item['score']}, "
          f"问题{item['findings_count']}个, "
          f"置信度{item['confidence']:.2f}")
```

**最佳实践**：

1. **数据验证**：调用前验证data_source格式是否符合7.2章节规范
2. **异常处理**：捕获`InvalidDataSourceError`等异常，提供用户友好的错误信息
3. **缓存利用**：相同数据的分析结果可缓存30分钟，避免重复计算
4. **异步调用**：对于Agent级分析（耗时较长），使用`analyze_async`方法
5. **结果验证**：检查返回结果的`confidence`字段，低置信度结果需要人工复核

### 7.6 置信度评估

Agent在分析完成后，会对分析结果的置信度进行评估（0.0-1.0），影响因素包括：

- **数据完整性** (30%)：输入数据是否完整，缺失字段比例
- **证据充分性** (25%)：问题证据是否充足，数据点数量
- **异常值检测** (20%)：是否存在明显异常数据
- **历史一致性** (15%)：与历史趋势是否一致
- **逻辑一致性** (10%)：分析逻辑是否合理

```python
def calculate_confidence(data_source, findings):
    """
    计算分析置信度
    """
    confidence = 0.0
    
    # 数据完整性评估
    completeness_score = calculate_data_completeness(data_source)
    confidence += completeness_score * 0.3
    
    # 证据充分性评估
    evidence_score = calculate_evidence_quality(findings)
    confidence += evidence_score * 0.25
    
    # 其他因子...
    
    return min(1.0, max(0.0, confidence))
```

### 7.7 异常处理

当输入数据不符合要求时，Agent返回错误信息：

```json
{
  "analysis_metadata": {
    "analysis_level": "agent",
    "timestamp": "2025-11-19T10:30:00Z"
  },
  "error": {
    "code": "INVALID_DATA_SOURCE",
    "message": "数据源格式不符合要求：缺少必要字段 agent_metrics",
    "details": {
      "missing_fields": ["agent_metrics"]
    }
  },
  "success": false
}
```

### 7.8 性能优化

- **异步分析**：对于Agent级分析（耗时较长），支持异步模式(基于resume 实现，本版本暂不支持)

### 7.9 质量保证

- **单元测试**：覆盖所有三种分析级别的典型场景
- **集成测试**：测试完整的数据输入到结果输出链路
- **准确性验证**：人工抽样验证分析准确性 > 80%
- **性能测试**：单次分析响应时间 < 3秒

## 8. 可视化设计（Dashboard）

建议四个核心看板：

- Agent Overview Dashboard & Qulity Insights

- Session Explorer & Qulity Insights

- Run Trace Viewer & Qulity Insights

## 9. 研发 Roadmap 与 Story 拆分

### 9.1 整体规划

**项目周期**：10个工作日（压缩至11天含测试验收）

**团队分工**：

- **可观测性建设（1-4）**：家祥负责，Day 1-7
- **质量分析建设（5-8）**：郭晨光负责，Day 2-10

**并行策略**：

- **3天并行期**：Day 3-5，家祥和郭晨光并行开发
- **关键点**：Story 1完成后即可启动Story 5（无强依赖）
- **优势**：质量分析引擎提前开发，整体周期从12天压缩至10-11天

### 9.2 开发路线图（Roadmap）

```
Day 1-2 (家祥):
├─ Story 1: agent & session & run 资源对象建模与生命周期管理

Day 3-4 (并行):
├─ Story 2: Agent 指标设计与埋点查询 (家祥)
├─ Story 3: Session 指标设计与埋点查询 (家祥)
└─ Story 5 开始: 质量分析 Agent 核心能力架构设计 (郭晨光)

Day 5-6 (并行):
├─ Story 4: Run Trace 设计、埋点和查询 (家祥)
└─ Story 5 继续: 核心分析逻辑实现 (郭晨光)

Day 7 (家祥完成可观测性):
└─ 可观测性建设完成，准备联调

Day 7-8 (郭晨光):
├─ Story 5 收尾: Prompt 设计与联调
├─ Story 6: Agent 级质量分析与优化建议

Day 8-10 (郭晨光):
├─ Story 7: Session 级质量分析与优化建议
└─ Story 8: Run 级质量分析与优化建议

Day 10-12 (全体):
├─ 集成测试
└─ 验收交付
```

**并行策略说明**：

- **3天并行期**：Day 3-5，家祥和郭晨光并行开发
- **关键依赖**：Story 1完成后，Story 5即可启动（无需等待Story 2-4完成）
- **优势**：质量分析引擎可提前开发，为后续集成留出更多缓冲时间
- **总工期压缩**：从12天缩短至10-11天

### 9.3 Story 详细拆分

---

#### Story 1: Agent/Session/Run 资源对象建模与管理
**负责人**: 家祥 | **预估时间**: 2天 | **优先级**: P0

**目标**: 建立 Agent → Session → Run → Progress 四层资源对象的完整生命周期管理体系

[Story-Agent/Session/Run 资源对象建模与管理](https://devops.aishu.cn/AISHUDevOps/DIP/_workitems/edit/793027)

**详细任务**:

1. **数据模型设计** (0.5天)
   - [ ] 设计 Agent 实体模型（agent_id, name, version, status, config等）
   - [ ] 设计 Session 实体模型（session_id, agent_id, user_id, start_time, end_time, status等）
   - [ ] 设计 Run 实体模型（run_id, session_id, request, response, start_time, end_time, status等）
   - [ ] 设计 Progress/Span 实体模型（span_id, run_id, parent_span_id, type, input, output, duration等）

2. **生命周期管理实现** (1天)
   - [ ] 实现 Agent 创建/更新/删除接口
   - [ ] 实现 Session 生命周期管理（创建、活跃、结束、超时处理）
   - [ ] 实现 Run 生命周期管理（创建、执行、记录、关联）
   - [ ] 实现 Progress 链路记录（嵌套结构、父子关系、顺序关联）

3. **OpenSearch 索引设计** (0.5天)
   - [ ] 设计 agent 索引模板（agent-index）
   - [ ] 设计 session 索引模板（session-index）
   - [ ] 设计 run 索引模板（run-index）
   - [ ] 设计 trace 索引模板（trace-index，包含嵌套对象）
   - [ ] 配置索引生命周期策略（ILM Policy）

**验收标准**:

- ✅ 能创建/查询/管理 Agent 资源
- ✅ 能跟踪 Session 从创建到结束的完整生命周期
- ✅ 能记录 Run 的详细执行过程
- ✅ 能在 OpenSearch 中查询指定 Agent 下的所有 Session
- ✅ 能在 OpenSearch 中查询指定 Session 下的所有 Run
- ✅ 数据查询延迟 < 500ms

---

#### Story 2: Agent 指标设计与埋点查询
**负责人**: 家祥 | **预估时间**: 1.5天 | **优先级**: P0

**目标**: 基于 OpenTelemetry 实现 Agent 级指标的自动埋点与查询

**详细任务**:

1. **指标定义实现** (0.5天)
   - [ ] 实现 Agent 聚合指标 Counter
     - total_requests（总请求数）
     - unique_users（独立用户数）
     - total_sessions（总会话数）
   - [ ] 实现 Agent 百分比指标 Histogram
     - avg_session_rounds（平均会话轮次）
     - response_time_p50/p90/p99（响应时间分位数）
     - ttft_duration_p50/p90/p99（首次响应耗时分位数）
   - [ ] 实现 Agent 状态指标 Gauge
     - task_success_rate（任务成功率）
     - agent_crash_rate（崩溃率）
     - tool_fail_rate（工具失败率）

2. **OpenTelemetry 埋点实现** (0.5天)
   - [ ] 在 chat 入口埋点：total_requests++
   - [ ] 在 session 创建/结束埋点：total_sessions
   - [ ] 在 tool 调用失败埋点：tool_fail_rate
   - [ ] 在 run 完成埋点：response_time, task_success
   - [ ] 在异常处理埋点：crash_rate

3. **指标导出与查询** (0.5天)
   - [ ] 集成 Prometheus Exporter（HTTP 拉取模式）
   - [ ] 配置指标标签（agent_id, agent_name, environment等）
   - [ ] 实现 Agent 指标聚合查询接口
   - [ ] 实现指标趋势分析（小时/天维度）

**验收标准**:

- ✅ Agent 关键指标能正常上报到监控系统
- ✅ 指标标签完整（agent_id, agent_name等）
- ✅ 指标数值准确（通过人工验证）
- ✅ 能在监控平台查看指标趋势图
- ✅ 指标查询接口响应时间 < 1s

---

#### Story 3: Session 指标设计与埋点查询
**负责人**: 家祥 | **预估时间**: 1.5天 | **优先级**: P0

**目标**: 实现 Session 级性能和质量指标的自动采集、存储和查询

**详细任务**:

1. **Session 指标设计** (0.5天)
   - [ ] 实现会话跟踪指标
     - session_run_count（会话总轮数）
     - session_duration（会话时长）
     - ⚠️ **注**：Session缺少完成状态字段，无法直接记录任务完成状态
   - [ ] 实现性能指标
     - avg_response_time（平均响应时间）
     - tool_error_count（工具错误次数）
   - [ ] 实现成本指标
     - session_cost（单会话成本）
     - cost_per_request（单次请求成本）

2. **埋点实现** (0.5天)
   - [ ] 在 session 创建时记录开始时间
   - [ ] 在每次 run 开始时记录轮次+1
   - [ ] 在 tool 调用时累积错误计数
   - [ ] 在 session 结束时计算总时长和成本
   - [ ] ⚠️ **注**：Session缺少完成状态字段，无法直接判定任务完成情况

3. **存储与查询** (0.5天)
   - [ ] Session 指标写入 session-index
   - [ ] 实现按 agent_id 查询 session 列表
   - [ ] 实现按 session_id 查询单次会话详情
   - [ ] 实现会话统计聚合查询（平均值、最大值、分布）

**验收标准**:

- ✅ Session 指标能正确记录和存储
- ✅ 能查询到指定 Agent 下的所有 Session
- ✅ 能查询到指定 Session 的完整指标
- ✅ 会话统计数据准确（通过采样验证）
- ✅ 查询接口性能满足要求（< 500ms）

---

#### Story 4: Run Trace 设计、埋点和查询
**负责人**: 家祥 | **预估时间**: 2天 | **优先级**: P0

**目标**: 实现 Run 级别的完整链路追踪，记录详细执行路径

**详细任务**:

1. **Trace 模型设计** (0.5天)
   - [ ] 定义 Trace/Span 结构（基于 OpenTelemetry 标准）
   - [ ] 设计 Progress 结构（Block、Stage、Span 层级关系）
   - [ ] 设计工具调用记录（tool_name, input, output, duration, status）
   - [ ] 设计模型调用记录（model_name, tokens_in, tokens_out, duration）

2. **链路追踪埋点** (1天)
   - [ ] Run 创建时生成 trace_id
   - [ ] 在 Agent 推理前后埋点（LLM span）
   - [ ] 在每次工具调用前后埋点（Tool span）
   - [ ] 在 Progress 阶段变更时埋点（Stage span）
   - [ ] 建立 Span 层级关系（parent-child chain）
   - [ ] 记录关键属性（model, tokens, tool_params, error 等）

3. **Trace 存储与查询** (0.5天)
   - [ ] Trace 数据写入 trace-index（嵌套结构）
   - [ ] 实现按 run_id 查询完整链路
   - [ ] 实现按 session_id 查询所有 run 的 trace
   - [ ] 实现时间范围查询（start_time - end_time）
   - [ ] 实现错误筛选（status=FAILED 的 trace）

**验收标准**:

- ✅ 每个 Run 都有完整的 trace_id
- ✅ Trace 包含所有关键阶段（LLM、Tool、Progress）
- ✅ 能查看 Run 的完整执行链路（可视化）
- ✅ 能定位到具体的失败点
- ✅ Trace 查询响应 < 1s

---

#### Story 5: 质量分析 Agent 实现方案设计
**负责人**: 郭晨光 | **预估时间**: 3天 | **优先级**: P0

**目标**: 构建专门的质量分析 Agent，能够自动分析 Agent/Session/Run 数据并生成质量报告

**并行开发说明**: Story 5可以在Story 1完成后立即启动，无需等待Story 2-4完成。质量分析引擎独立开发，后期通过Mock数据进行联调。

**详细任务**:

1. **质量分析引擎架构设计** (1天)
   - [ ] 定义质量分析 Agent 数据模型
     - 输入：Agent/Session/Run 数据 + 指标
     - 处理：质量分析引擎
     - 输出：质量报告 + 优化建议
   - [ ] 设计分析维度框架
     - 性能分析（延迟、吞吐量、瓶颈）
     - 质量分析（正确性、一致性、幻觉率）
     - 用户体验分析（满意度、完成率）
     - 成本分析（Token 消耗、API 调用成本）
     - 可靠性分析（错误率、成功率）

2. **核心分析逻辑实现** (1.5天)
   - [ ] 性能瓶颈识别算法
     - 延迟分解（模型延迟 vs 工具延迟 vs 网络延迟）
     - 异常值检测（p99 延迟异常）
     - 慢请求聚类分析
   - [ ] 质量问题检测算法
     - 事实一致性检查
     - 逻辑矛盾检测
     - 幻觉风险评估
     - 工具调用错误分析
   - [ ] 用户满意度评估算法
     - 显式反馈解析（点赞/点踩/评分）
     - 隐式行为分析（重试次数、对话轮次、放弃率）

3. **质量分析 Agent Prompt 设计** (0.5天)
   - [ ] 设计角色定位 Prompt（质量分析专家）
   - [ ] 设计分析流程 Prompt（分步骤执行）
   - [ ] 设计输出格式 Prompt（结构化 JSON）
   - [ ] 设计建议生成 Prompt（可执行建议）

**验收标准**:

- ✅ 质量分析 Agent 能成功启动和运行
- ✅ 能接收并解析 Agent/Session/Run 数据
- ✅ 能从 5 个维度进行全面分析
- ✅ 输出的质量报告结构化、可读
- ✅ 分析结果准确率 > 80%（人工抽样验证）
- ✅ 支持通过Mock数据进行独立开发和测试

---

#### Story 6: 基于质量分析 Agent 实现 Agent 级质量分析和优化建议
**负责人**: 郭晨光 | **预估时间**: 1天 | **优先级**: P1

**目标**: 在质量分析 Agent 基础上，实现 Agent 级别的质量分析，输出宏观优化建议

**详细任务**:

1. **Agent 级分析策略** (0.5天)
   - [ ] 定义 Agent 级分析指标
     - 全局成功率趋势
     - 用户满意度分布
     - 工具稳定性评估
     - 性能瓶颈排名
   - [ ] 设计异常检测算法
     - 成功率骤降检测
     - 用户满意度骤降检测
     - 错误率峰值检测

2. **分析逻辑实现** (0.3天)
   - [ ] 实现多时间窗口对比分析（1小时 vs 24小时 vs 7天）
   - [ ] 实现用户群体分析（新用户 vs 老用户）
   - [ ] 实现场景聚类分析（不同任务的性能差异）

3. **优化建议生成** (0.2天)
   - [ ] 生成工具优化建议
     - 识别不稳定工具 → 建议增强容错
     - 识别高频工具 → 建议缓存优化
   - [ ] 生成性能优化建议
     - 识别慢请求 → 建议启用 Streaming
     - 识别模型切换建议 → 建议调整模型配置
   - [ ] 生成配置优化建议
     - 识别内存使用低效 → 建议优化上下文长度
     - 识别重复调用 → 建议启用结果缓存

**验收标准**:

- ✅ 能自动检测 Agent 级别的异常指标
- ✅ 能输出结构化的 Agent 质量报告
- ✅ 优化建议具体可执行（有明确操作步骤）
- ✅ 能对比历史数据展示趋势变化
- ✅ 分析报告能导出为 PDF/HTML 格式

---

#### Story 7: 基于质量分析 Agent 实现 Session 级质量分析和优化建议
**负责人**: 郭晨光 | **预估时间**: 1天 | **优先级**: P1

**目标**: 实现 Session 级别的深度分析，识别单次对话的质量问题和改进方向

**详细任务**:

1. **Session 级分析策略** (0.5天)
   - [ ] 定义 Session 级分析维度
     - 对话流畅性（轮次合理性、对话连贯性）
     - 任务完成度（目标达成、用户满意度）
     - 问题识别（中断原因、失败点定位）
   - [ ] 设计对话质量评分模型
     - 相关性评分（回答与问题的匹配度）
     - 完整性评分（是否完全解答用户问题）
     - 清晰度评分（回答是否容易理解）

2. **分析逻辑实现** (0.3天)
   - [ ] 实现对话轮次分析
     - 轮次过高 → 可能提示词不清晰
     - 轮次过低 → 可能回答过于简单
     - 重复提问 → 可能回答质量不高
   - [ ] 实现中断点分析
     - 用户主动结束 → 可能满意度不高
     - 系统超时结束 → 可能性能问题
     - 错误退出 → 可能存在 bug

3. **优化建议生成** (0.2天)
   - [ ] 生成提示词优化建议
     - 识别歧义问题 → 建议澄清策略
     - 识别回答不完整 → 建议增加验证步骤
   - [ ] 生成知识库增强建议
     - 识别知识盲区 → 建议补充文档
     - 识别频繁查询 → 建议知识库优化

**验收标准**:

- ✅ 能为每个 Session 生成质量评分（0-100）
- ✅ 能定位到具体的问题阶段（哪个轮次、哪次工具调用）
- ✅ 能识别对话中断的原因并分类
- ✅ 优化建议针对性强（具体到某个问题）
- ✅ 能批量分析 Session 并生成汇总报告

---

#### Story 8: 基于质量分析 Agent 实现 Run 级质量分析和优化建议
**负责人**: 郭晨光 | **预估时间**: 2天 | **优先级**: P1

**目标**: 实现 Run 级别的精细化分析，输出最精准的优化建议

**详细任务**:

1. **Run 级分析策略** (0.5天)
   - [ ] 定义 Run 级分析指标
     - 输出质量（准确性、相关性、完整性）
     - 幻觉检测（事实核验、一致性检查）
     - 工具使用（调用是否必要、参数是否正确）
     - Token 效率（输入输出长度、冗余度）
   - [ ] 设计事实核验模型
     - 提取 Run 输出中的事实陈述
     - 对比知识库验证真实性
     - 标记不确定或疑似幻觉的内容

2. **分析逻辑实现** (1天)
   - [ ] 实现输入质量分析
     - 问题清晰度评估（是否有歧义）
     - 上下文完整性评估（是否包含必要信息）
     - 问题类型分类（事实性问题 vs 创意性问题）
   - [ ] 实现输出质量分析
     - 准确性检查（与事实库对比）
     - 相关性检查（与问题匹配度）
     - 完整性检查（是否完整回答）
     - 清晰度检查（是否结构化、易理解）
   - [ ] 实现工具调用分析
     - 调用必要性判断（是否有更简单的解决方案）
     - 调用效率评估（是否多次调用相似工具）
     - 参数正确性检查（工具返回是否与预期一致）

3. **优化建议生成** (0.5天)
   - [ ] 生成 Run 级 Prompt 优化建议
     - 识别模糊指令 → 建议更具体的描述
     - 识别缺少示例 → 建议增加 few-shot
   - [ ] 生成工具优化建议
     - 识别工具调用过深 → 建议简化流程
     - 识别错误参数 → 建议增加参数校验
   - [ ] 生成模型选择建议
     - 识别推理能力不足 → 建议切换更强模型
     - 识别成本过高 → 建议使用更经济模型

**验收标准**:

- ✅ 能为每个 Run 输出详细的质量分析报告
- ✅ 幻觉检测准确率 > 85%（人工标注验证）
- ✅ 能精确定位到具体的错误点（工具名、参数、阶段）
- ✅ 优化建议准确度高（人工评估相关性 > 90%）
- ✅ 支持批量 Run 分析并生成趋势图

### 9.4 关键依赖与风险

#### 技术依赖

- **OpenSearch**: 分布式搜索引擎（数据存储、查询）
- **OpenTelemetry**: 链路追踪和指标采集
- **Prometheus**: 指标监控和报警
- **质量分析 LLM**: 用于自动质量分析（建议使用 GPT-4 或 Claude）

#### 潜在风险与应对

1. **数据存储性能风险**
   - 风险：OpenSearch 查询性能不足
   - 应对：分片策略优化、索引预构建、结果缓存

2. **链路追踪开销风险**
   - 风险：Trace 埋点影响性能
   - 应对：采样率控制、异步写入、关键链路优先

3. **质量分析准确性风险**
   - 风险：LLM 分析结果不够准确
   - 应对：多模型对比、人工校验、持续优化 Prompt

4. **并行开发风险**
   - 风险：Story 5依赖后期真实数据进行联调，可能出现接口不匹配
   - 应对：提前定义清晰的数据接口规范，Story 5使用Mock数据开发，Day 7集中联调

### 9.5 测试与验收

#### 测试策略

1. **单元测试**: 覆盖核心算法（指标计算、异常检测）
2. **Mock测试**: 质量分析引擎通过Mock数据独立测试（支持Day 2-6并行开发）
3. **集成测试**: Day 7开始，测试端到端链路（埋点 → 存储 → 查询 → 分析）
4. **压力测试**: 模拟高并发场景（1000 QPS）
5. **准确性测试**: 人工标注数据集验证分析准确性

#### 验收标准

- **功能完整性**: 所有 Story 完成且验收通过
- **并行开发**: Story 5与Story 2-4实现3天并行开发，无明显依赖阻塞
- **接口对接**: Day 7集中联调完成，Mock数据与真实数据无缝切换
- **性能指标**: 查询响应 < 1s，埋点开销 < 5%
- **准确性指标**: 质量分析准确率 > 80%
- **用户体验**: 可视化界面友好、操作流畅
- **文档完整性**: API 文档、用户手册、运维指南齐全

### 9.6 项目里程碑

- **Day 2 里程碑**: 完成基础资源管理（Story 1），质量分析Agent启动（Story 5）
- **Day 4 里程碑**: 完成Agent/Session指标（Story 2-3），质量分析引擎架构设计完成
- **Day 6 里程碑**: 完成链路追踪（Story 4），质量分析核心逻辑完成
- **Day 7 里程碑**: 可观测性建设全部完成（Story 1-4），质量分析引擎联调完成
- **Day 8 里程碑**: 完成Agent级质量分析（Story 6）
- **Day 10 里程碑**: 完成全部功能（Story 7-8），准备交付
- **Day 12 里程碑**: 完成测试验收，上线发布

**关键路径说明**：
- **家祥关键路径**：Story 1 → Story 2-3 → Story 4 → 联调（Day 7完成）
- **郭晨光关键路径**：Story 5（独立开发）→ Story 6-8（依赖Story 5完成）
- **并行优势**：利用Story 1与Story 5无依赖关系，实现3天并行开发，整体周期压缩
