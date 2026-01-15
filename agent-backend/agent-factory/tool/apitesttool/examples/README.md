# API测试工具示例

本目录包含了各种使用场景的示例，帮助您快速了解和使用API测试工具包。

## 目录结构

```
examples/
├── README.md                    # 本文档
├── basic_usage.go              # 基础使用示例
├── advanced/                   # 高级功能示例
│   └── main.go
├── performance/                # 性能测试示例
│   └── main.go
├── config/                     # 配置文件示例
│   └── main.go
└── errors/                     # 错误处理示例
    └── main.go
```

## 示例说明

### 1. 基础使用示例 (`basic_usage.go`)

演示API测试工具的基础功能：

- **简单GET请求测试**: 最基本的API请求测试
- **POST请求测试**: 带请求体的POST请求
- **带断言的测试**: 使用断言验证响应内容
- **从配置文件加载测试**: 使用JSON配置文件定义测试

**运行方式:**
```bash
cd examples
go run basic_usage.go
```

**主要功能:**
- `apitest.QuickTest()` - 快速测试单个API
- `apitest.WithHeaders()` - 设置请求头
- `apitest.WithBody()` - 设置请求体
- `apitest.WithTimeout()` - 设置超时时间
- `apitest.WithAssertions()` - 添加断言
- `tester.LoadConfigFromString()` - 从字符串加载配置

### 2. 高级功能示例 (`advanced/main.go`)

展示高级功能的使用：

- **动态变量使用**: UUID、时间戳、随机数、随机字符串、随机姓名
- **变量提取功能**: 从响应中提取变量供后续测试使用
- **链式测试**: 多个测试之间的变量传递
- **变量管理器直接使用**: 自定义变量配置和管理

**运行方式:**
```bash
cd examples/advanced
go run main.go
```

**主要功能:**
- 动态变量: `${uuid}`, `${timestamp}`, `${random_number:1-100}`, `${random_string:8}`, `${random_name:6}`
- 变量提取: 从响应体、响应头、状态码提取数据
- 变量管理: `tester.SetVariable()`, `tester.GetVariable()`, `tester.GetAllVariables()`
- 自定义配置: `apitest.NewVariableManagerWithConfig()`

**动态变量详细说明:**

| 变量类型 | 语法 | 说明 | 示例 |
|---------|------|------|------|
| UUID | `${uuid}` | 生成UUID | `550e8400-e29b-41d4-a716-446655440000` |
| 时间戳 | `${timestamp}` | Unix时间戳（秒） | `1640995200` |
| 毫秒时间戳 | `${timestamp_ms}` | Unix时间戳（毫秒） | `1640995200000` |
| 随机数 | `${random_number}` | 默认范围随机数 | `42` |
| 自定义范围随机数 | `${random_number:min-max}` | 指定范围随机数 | `${random_number:1-100}` |
| 随机字符串 | `${random_string}` | 默认长度随机字符串 | `aBc123XyZ` |
| 自定义长度随机字符串 | `${random_string:length}` | 指定长度随机字符串 | `${random_string:12}` |
| 随机姓名 | `${random_name}` | 默认长度随机姓名 | `JohnSmith` |
| 自定义长度随机姓名 | `${random_name:length}` | 指定长度随机姓名 | `${random_name:10}` |

**变量提取详细说明:**

变量提取支持从以下源提取数据：
- `body`: 从响应体提取（支持JSONPath）
- `header`: 从响应头提取
- `status_code`: 从状态码提取

提取方式：
- **JSONPath**: 使用点号分隔的路径，如 `data.0.id`
- **正则表达式**: 使用regex字段进行正则匹配提取

### 3. 性能测试示例 (`performance/main.go`)

演示性能测试和负载测试：

- **并发性能测试**: 串行vs并发执行的性能对比
- **负载测试**: 模拟不同数量的并发用户
- **压力测试**: 测试系统在高负载下的表现
- **响应时间分析**: 分析不同延迟场景的响应时间

**运行方式:**
```bash
cd examples/performance
go run main.go
```

**主要功能:**
- `apitest.WithParallel()` - 设置并发数
- 性能指标计算: 响应时间、吞吐量、成功率
- 百分位数计算: P95、P99响应时间
- 统计分析: 平均值、最小值、最大值、标准差

**性能测试场景:**
1. **串行执行**: 顺序执行所有测试，测量基准性能
2. **并发执行**: 并行执行测试，对比性能提升
3. **负载测试**: 模拟100个并发用户的负载
4. **压力测试**: 测试系统在高并发下的稳定性

### 4. 配置文件示例 (`config/main.go`)

展示各种配置文件格式和用法：

- **JSON配置文件**: 标准JSON格式配置
- **YAML配置文件**: YAML格式配置
- **复杂配置**: 包含变量提取、链式测试的复杂场景
- **环境配置**: 多环境配置管理

**运行方式:**
```bash
cd examples/config
go run main.go
```

**主要功能:**
- `tester.LoadConfigFromFile()` - 从文件加载配置
- `tester.LoadConfigFromString()` - 从字符串加载配置
- 支持JSON和YAML格式
- 环境变量管理
- 复杂测试场景配置

**配置文件特性:**
- **全局变量**: 在配置文件顶层定义变量，所有测试共享
- **局部变量**: 在单个测试中定义变量，仅该测试使用
- **动态变量配置**: 自定义随机数范围、字符串长度等
- **变量提取链**: 前一个测试的输出作为后一个测试的输入

### 5. 错误处理示例 (`errors/main.go`)

演示各种错误场景的处理：

- **网络错误处理**: 无效URL、连接拒绝等网络问题
- **超时错误处理**: 请求超时的处理
- **状态码错误处理**: HTTP错误状态码的处理
- **断言失败处理**: 断言失败时的错误信息

**运行方式:**
```bash
cd examples/errors
go run main.go
```

**主要功能:**
- 网络错误捕获和处理
- 超时设置和错误处理
- HTTP状态码验证
- 断言失败分析

**错误处理场景:**
1. **网络不可达**: 测试无效域名的处理
2. **连接超时**: 测试连接超时的处理
3. **HTTP错误**: 测试4xx、5xx状态码的处理
4. **断言失败**: 测试断言失败时的详细错误信息
5. **可选断言**: 演示可选断言不影响整体结果

## 快速开始

1. **安装依赖**:
   ```bash
   cd /path/to/agent-go-common-pkg/tool/apitesttool
   go mod tidy
   ```

2. **运行基础示例**:
   ```bash
   cd examples
   go run basic_usage.go
   ```

3. **运行特定示例**:
   ```bash
   # 高级功能示例
   cd examples/advanced && go run main.go
   
   # 性能测试示例
   cd examples/performance && go run main.go
   
   # 配置文件示例
   cd examples/config && go run main.go
   
   # 错误处理示例
   cd examples/errors && go run main.go
   ```

## 常用API参考

### 快速测试
```go
result := apitest.QuickTest("GET", "https://api.example.com/users",
    apitest.WithHeaders(map[string]string{
        "Authorization": "Bearer token",
    }),
    apitest.WithTimeout(30*time.Second),
    apitest.WithExpectedStatus(200),
    apitest.WithAssertions(
        apitest.CreateAssertion("exists", "body.data", nil, "应该有data字段"),
        apitest.CreateAssertion("greater_than", "body.data.length", 0, "数据不应为空"),
    ),
)
```

### 配置文件测试
```go
tester := apitest.New()
config, err := tester.LoadConfigFromFile("test_config.json")
if err != nil {
    log.Fatal(err)
}

report, err := tester.RunTests(config, 
    apitest.WithVerbose(true),
    apitest.WithParallel(5),
)
```

### 动态变量使用
```go
// 在配置文件或请求中使用
{
    "headers": {
        "X-Request-ID": "${uuid}",
        "X-Timestamp": "${timestamp}"
    },
    "body": {
        "user_id": "${random_number:1000-9999}",
        "username": "${random_string:8}",
        "email": "${random_string:6}@test.com",
        "phone": "${random_number:1000000000-9999999999}",
        "display_name": "${random_name:10}",
        "created_at": "${timestamp_ms}"
    }
}
```

### 变量提取和链式测试
```go
{
    "tests": [
        {
            "name": "步骤1: 创建资源",
            "request": {
                "method": "POST",
                "url": "https://api.example.com/resources",
                "body": {
                    "name": "${random_string:10}",
                    "type": "test"
                }
            },
            "variable_extraction": [
                {
                    "name": "resource_id",
                    "source": "body",
                    "path": "id"
                },
                {
                    "name": "resource_name",
                    "source": "body",
                    "path": "name"
                }
            ]
        },
        {
            "name": "步骤2: 使用提取的变量",
            "request": {
                "method": "GET",
                "url": "https://api.example.com/resources/{{resource_id}}"
            },
            "expected": {
                "assertions": [
                    {
                        "type": "equals",
                        "field": "body.name",
                        "value": "{{resource_name}}",
                        "message": "资源名称应该匹配"
                    }
                ]
            }
        }
    ]
}
```

### 变量管理器直接使用
```go
// 创建自定义配置的变量管理器
config := apitest.VariableConfig{
    RandomNumberMin:    100,
    RandomNumberMax:    999,
    RandomStringLength: 15,
    RandomNameLength:   12,
}

vm := apitest.NewVariableManagerWithConfig(config)

// 设置变量
vm.SetVariables(map[string]string{
    "api_base": "https://api.example.com",
    "api_key":  "your-api-key",
})

// 替换变量
result := vm.ReplaceVariables("用户ID: ${random_number}, API: {{api_base}}")

// 从响应中提取变量
extractions := []apitest.VariableExtraction{
    {Name: "user_id", Source: "body", Path: "id"},
    {Name: "email_domain", Source: "body", Path: "email", Regex: "@(.+)$"},
}
err := vm.ExtractVariables(extractions, response)
```

### 高级断言
```go
// 创建各种类型的断言
assertions := []apitest.AssertionConfig{
    // 基础断言
    apitest.CreateAssertion("equals", "body.status", "success", "状态应该是success"),
    apitest.CreateAssertion("contains", "body.message", "操作成功", "消息应该包含成功提示"),
    apitest.CreateAssertion("exists", "body.data", nil, "应该有data字段"),
    
    // 数值比较断言
    apitest.CreateAssertion("greater_than", "body.count", 0, "数量应该大于0"),
    apitest.CreateAssertion("less_equal", "body.count", 100, "数量应该不超过100"),
    
    // 正则表达式断言
    apitest.CreateAssertion("regex", "body.email", "^[\\w-\\.]+@([\\w-]+\\.)+[\\w-]{2,4}$", "邮箱格式应该正确"),
    
    // 可选断言（失败不影响整体结果）
    apitest.CreateOptionalAssertion("exists", "body.optional_field", nil, "可选字段可能存在"),
}
```

## 高级使用技巧

### 1. 环境配置管理
```go
// 根据环境变量选择不同的配置
env := os.Getenv("TEST_ENV")
if env == "" {
    env = "dev"
}

configFile := fmt.Sprintf("config_%s.json", env)
config, err := tester.LoadConfigFromFile(configFile)
```

### 2. 数据驱动测试
```go
// 使用外部数据文件驱动测试
testData := []struct {
    UserID   string
    Expected int
}{
    {"user1", 200},
    {"user2", 200},
    {"invalid", 404},
}

for _, data := range testData {
    result := apitest.QuickTest("GET", 
        fmt.Sprintf("https://api.example.com/users/%s", data.UserID),
        apitest.WithExpectedStatus(data.Expected),
    )
    // 处理结果...
}
```

### 3. 自定义报告处理
```go
report, err := tester.RunTests(config)
if err != nil {
    log.Fatal(err)
}

// 自定义报告处理
for _, result := range report.Results {
    if !result.Success {
        log.Printf("测试失败: %s - %s", result.TestName, result.Error)
        // 发送告警通知...
    }
}

// 生成多种格式报告
reporter := apitest.NewReporter()
reporter.GenerateReport(report, "html", "report.html")
reporter.GenerateReport(report, "json", "report.json")
```

### 4. 性能监控集成
```go
// 记录性能指标
var totalDuration time.Duration
var successCount, failCount int

for _, result := range report.Results {
    totalDuration += result.Duration
    if result.Success {
        successCount++
    } else {
        failCount++
    }
}

avgDuration := totalDuration / time.Duration(len(report.Results))
successRate := float64(successCount) / float64(len(report.Results)) * 100

log.Printf("平均响应时间: %v", avgDuration)
log.Printf("成功率: %.2f%%", successRate)
```

## 注意事项

1. **网络依赖**: 示例中使用了外部API服务（如httpbin.org），需要网络连接
2. **超时设置**: 根据网络环境调整超时时间
3. **并发限制**: 性能测试时注意不要对目标服务造成过大压力
4. **错误处理**: 生产环境中要做好错误处理和日志记录
5. **变量作用域**: 理解全局变量、局部变量和提取变量的作用域
6. **动态变量性能**: 大量使用动态变量可能影响性能，合理使用

## 扩展示例

您可以基于这些示例创建自己的测试场景：

1. **自定义断言**: 创建特定业务逻辑的断言
2. **数据驱动测试**: 使用外部数据文件驱动测试
3. **集成测试**: 结合数据库、消息队列等的集成测试
4. **监控告警**: 结合监控系统的API健康检查
5. **CI/CD集成**: 在持续集成流水线中使用API测试
6. **多环境测试**: 针对不同环境的自动化测试

## 问题反馈

如果您在使用过程中遇到问题或有改进建议，请通过以下方式反馈：

1. 查看项目文档
2. 检查示例代码
3. 提交Issue或Pull Request 