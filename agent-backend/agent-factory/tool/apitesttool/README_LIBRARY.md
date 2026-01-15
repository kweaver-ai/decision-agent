# API测试工具库

这是一个功能强大的Go语言API测试工具库，既可以作为独立的命令行工具使用，也可以作为库集成到其他Go项目中。

## 特性

- 🚀 **双重用途**: 既可作为命令行工具，也可作为Go库使用
- 📝 **多种配置格式**: 支持JSON和YAML配置文件
- 🔧 **灵活的断言系统**: 支持23种断言类型（包含别名），包括JSONPath断言和type类型检查
- ⚡ **并发执行**: 支持并行执行测试，提高效率
- 🔄 **重试机制**: 支持失败重试，提高测试稳定性
- 📊 **多格式报告**: 支持控制台、JSON、HTML三种报告格式
- 🔗 **动态变量**: 支持UUID、时间戳、随机数等动态变量生成
- 🔄 **变量提取**: 支持从响应中提取变量供后续测试使用
- 🔗 **链式测试**: 支持测试用例间的变量传递和依赖
- ⏱️ **超时控制**: 可配置每个测试的超时时间
- 🎯 **可选断言**: 支持可选断言，不影响整体测试结果

## 作为库使用

### 安装

```bash
go get devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/tool/apitesttool/apitest
```

### 快速开始

#### 1. 快速测试单个API

```go
package main

import (
    "fmt"
    "devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/tool/apitesttool/apitest"
)

func main() {
    // 快速测试一个API端点
    result := apitest.QuickTest("GET", "https://api.example.com/users/1",
        apitest.WithExpectedStatus(200),
        apitest.WithHeaders(map[string]string{
            "Accept": "application/json",
        }),
        apitest.WithAssertions(
            apitest.CreateAssertion("exists", "body.id", nil, "用户应该有ID"),
            apitest.CreateAssertion("equals", "body.name", "John", "用户名应该是John"),
            apitest.CreateAssertion("not_equals", "body.status", "deleted", "用户状态不应该是已删除"),
            apitest.CreateAssertion("not_contains", "body.email", "temp", "邮箱不应该包含临时标识"),
            apitest.CreateAssertion("starts_with", "body.username", "user_", "用户名应该以user_开头"),
            apitest.CreateAssertion("length_greater_than", "body.description", 10, "描述长度应该大于10"),
            apitest.CreateAssertion("in", "body.role", []interface{}{"admin", "user", "guest"}, "角色应该在允许列表中"),
            apitest.CreateAssertion("greater_than_or_equal", "body.age", 18, "年龄应该大于等于18（使用别名）"),
        ),
    )

    if result.Success {
        fmt.Println("✓ 测试通过")
    } else {
        fmt.Println("✗ 测试失败")
        fmt.Printf("错误: %s\n", result.Error)
    }
    
    fmt.Printf("耗时: %v\n", result.Duration)
    fmt.Printf("状态码: %d\n", result.Response.StatusCode)
}
```

#### 2. 使用配置文件

```go
package main

import (
    "log"
    "devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/tool/apitesttool/apitest"
)

func main() {
    // 创建API测试器
    tester := apitest.New()
    
    // 从文件加载配置
    config, err := tester.LoadConfigFromFile("test_config.json")
    if err != nil {
        log.Fatal(err)
    }

    // 执行测试
    report, err := tester.RunTests(config, 
        apitest.WithParallel(3),    // 3个并发
        apitest.WithVerbose(true),  // 详细输出
    )
    if err != nil {
        log.Fatal(err)
    }

    // 打印控制台报告
    reporter := apitest.NewReporter()
    reporter.PrintConsoleReport(report)
    
    // 生成HTML报告
    err = reporter.GenerateReport(report, "html", "test_report.html")
    if err != nil {
        log.Printf("生成HTML报告失败: %v", err)
    }
}
```

#### 3. 从字符串配置创建测试

```go
package main

import (
    "log"
    "devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/tool/apitesttool/apitest"
)

func main() {
    tester := apitest.New()
    
    configJSON := `{
        "name": "动态API测试",
        "description": "通过字符串配置创建的测试",
        "tests": [
            {
                "name": "测试用户API",
                "request": {
                    "method": "GET",
                    "url": "https://jsonplaceholder.typicode.com/users/{{user_id}}"
                },
                "expected": {
                    "status_code": 200,
                    "assertions": [
                        {
                            "type": "exists",
                            "field": "body.id",
                            "message": "用户应该有ID"
                        }
                    ]
                },
                "variables": {
                    "user_id": "1"
                },
                "timeout": "10s"
            }
        ]
    }`
    
    config, err := tester.LoadConfigFromString(configJSON, "json")
    if err != nil {
        log.Fatal(err)
    }
    
    report, err := tester.RunTests(config)
    if err != nil {
        log.Fatal(err)
    }
    
    reporter := apitest.NewReporter()
    reporter.PrintConsoleReport(report)
}
```

#### 4. 单个测试用例

```go
package main

import (
    "fmt"
    "time"
    "devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/tool/apitesttool/apitest"
)

func main() {
    tester := apitest.New()
    
    test := apitest.APITest{
        Name: "自定义POST测试",
        Request: apitest.RequestConfig{
            Method: "POST",
            URL:    "https://jsonplaceholder.typicode.com/posts",
            Headers: map[string]string{
                "Content-Type": "application/json",
            },
            Body: map[string]interface{}{
                "title":  "测试文章",
                "body":   "这是测试内容",
                "userId": 1,
            },
        },
        Expected: apitest.ExpectedResponse{
            StatusCode: 201,
            Assertions: []apitest.AssertionConfig{
                {
                    Type:    "exists",
                    Field:   "body.id",
                    Message: "创建的文章应该有ID",
                },
                {
                    Type:    "equals",
                    Field:   "body.title",
                    Value:   "测试文章",
                    Message: "文章标题应该匹配",
                },
            },
        },
        Timeout: apitest.Duration(10 * time.Second),
        Retry:   2,
    }
    
    result := tester.RunSingleTest(test)
    fmt.Printf("测试结果: %v\n", result.Success)
    fmt.Printf("响应状态码: %d\n", result.Response.StatusCode)
    fmt.Printf("响应大小: %d bytes\n", result.Response.Size)
    
    if !result.Success {
        fmt.Printf("错误: %s\n", result.Error)
    }
}
```

#### 5. 批量测试和报告生成

```go
package main

import (
    "log"
    "devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/tool/apitesttool/apitest"
)

func main() {
    tester := apitest.New()
    
    // 创建测试配置
    config := &apitest.TestConfig{
        Name:        "批量API测试",
        Description: "演示批量测试和报告生成",
        Tests: []apitest.APITest{
            {
                Name: "测试GET请求",
                Request: apitest.RequestConfig{
                    Method: "GET",
                    URL:    "https://jsonplaceholder.typicode.com/users/1",
                },
                Expected: apitest.ExpectedResponse{
                    StatusCode: 200,
                    Assertions: []apitest.AssertionConfig{
                        {
                            Type:    "exists",
                            Field:   "body.id",
                            Message: "用户应该有ID",
                        },
                    },
                },
            },
            {
                Name: "测试POST请求",
                Request: apitest.RequestConfig{
                    Method: "POST",
                    URL:    "https://jsonplaceholder.typicode.com/posts",
                    Headers: map[string]string{
                        "Content-Type": "application/json",
                    },
                    Body: map[string]interface{}{
                        "title":  "测试文章",
                        "body":   "测试内容",
                        "userId": 1,
                    },
                },
                Expected: apitest.ExpectedResponse{
                    StatusCode: 201,
                    Assertions: []apitest.AssertionConfig{
                        {
                            Type:    "exists",
                            Field:   "body.id",
                            Message: "创建的文章应该有ID",
                        },
                    },
                },
            },
        },
    }

    // 执行测试
    report, err := tester.RunTests(config, apitest.WithVerbose(true))
    if err != nil {
        log.Fatal(err)
    }

    // 生成多种格式的报告
    reporter := apitest.NewReporter()
    
    // 控制台报告
    reporter.PrintConsoleReport(report)
    
    // JSON报告
    err = reporter.GenerateReport(report, "json", "test_report.json")
    if err != nil {
        log.Printf("生成JSON报告失败: %v", err)
    }
    
    // HTML报告
    err = reporter.GenerateReport(report, "html", "test_report.html")
    if err != nil {
        log.Printf("生成HTML报告失败: %v", err)
    }
}
```

### API参考

#### 主要类型

- `APITester`: 主要的测试器接口
- `TestConfig`: 测试配置结构
- `APITest`: 单个测试用例
- `TestResult`: 测试结果
- `TestReport`: 测试报告
- `Reporter`: 报告生成器

#### 主要方法

##### APITester 方法
- `New()`: 创建新的API测试器
- `LoadConfigFromFile(path)`: 从文件加载配置
- `LoadConfigFromString(data, format)`: 从字符串加载配置
- `RunTests(config, options...)`: 执行测试套件
- `RunSingleTest(test)`: 执行单个测试

##### Reporter 方法
- `NewReporter()`: 创建新的报告生成器
- `GenerateReport(report, format, output)`: 生成报告
- `PrintConsoleReport(report)`: 打印控制台报告

##### 快速测试方法
- `QuickTest(method, url, options...)`: 快速测试API

#### 快速测试选项

- `WithHeaders(headers)`: 设置请求头
- `WithBody(body)`: 设置请求体
- `WithParams(params)`: 设置URL参数
- `WithTimeout(duration)`: 设置超时时间
- `WithExpectedStatus(code)`: 设置期望状态码
- `WithAssertions(assertions...)`: 设置断言
- `WithVariables(variables)`: 设置变量

#### 执行选项

- `WithParallel(count)`: 设置并发数
- `WithVerbose(enabled)`: 设置详细输出

#### 断言创建

```go
// 创建断言的辅助函数
assertion := apitest.CreateAssertion("equals", "body.id", 1, "用户ID应该是1")
optionalAssertion := apitest.CreateOptionalAssertion("contains", "body.name", "test", "名称可能包含test")
```

#### 断言类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `equals` | 值相等 | `CreateAssertion("equals", "body.id", 1, "ID应该是1")` |
| `not_equals` | 值不相等 | `CreateAssertion("not_equals", "body.status", "error", "状态不应该是error")` |
| `contains` | 包含字符串 | `CreateAssertion("contains", "body.name", "test", "名称应该包含test")` |
| `not_contains` | 不包含字符串 | `CreateAssertion("not_contains", "body.message", "error", "消息不应该包含error")` |
| `regex` | 正则表达式匹配 | `CreateAssertion("regex", "body.email", "^[\\w-\\.]+@([\\w-]+\\.)+[\\w-]{2,4}$", "邮箱格式")` |
| `exists` | 字段存在 | `CreateAssertion("exists", "body.data", nil, "应该有data字段")` |
| `not_exists` | 字段不存在 | `CreateAssertion("not_exists", "body.error", nil, "不应该有error字段")` |
| `greater_than` | 大于 | `CreateAssertion("greater_than", "body.count", 0, "数量应该大于0")` |
| `less_than` | 小于 | `CreateAssertion("less_than", "body.count", 100, "数量应该小于100")` |
| `greater_equal` | 大于等于 | `CreateAssertion("greater_equal", "body.score", 60, "分数应该>=60")` |
| `greater_than_or_equal` | 大于等于（别名） | `CreateAssertion("greater_than_or_equal", "body.score", 60, "分数应该>=60")` |
| `less_equal` | 小于等于 | `CreateAssertion("less_equal", "body.score", 100, "分数应该<=100")` |
| `less_than_or_equal` | 小于等于（别名） | `CreateAssertion("less_than_or_equal", "body.score", 100, "分数应该<=100")` |
| `type` | 类型检查 | `CreateAssertion("type", "body.id", "string", "ID应该是字符串类型")` |
| `starts_with` | 字符串以指定内容开头 | `CreateAssertion("starts_with", "body.name", "user_", "用户名应该以user_开头")` |
| `ends_with` | 字符串以指定内容结尾 | `CreateAssertion("ends_with", "body.email", "@example.com", "邮箱应该以@example.com结尾")` |
| `empty` | 值为空 | `CreateAssertion("empty", "body.description", nil, "描述应该为空")` |
| `not_empty` | 值不为空 | `CreateAssertion("not_empty", "body.data", nil, "数据不应该为空")` |
| `length` | 长度等于指定值 | `CreateAssertion("length", "body.items", 5, "项目数量应该是5")` |
| `length_greater_than` | 长度大于指定值 | `CreateAssertion("length_greater_than", "body.list", 0, "列表长度应该大于0")` |
| `length_less_than` | 长度小于指定值 | `CreateAssertion("length_less_than", "body.name", 50, "名称长度应该小于50")` |
| `length_greater_equal` | 长度大于等于指定值 | `CreateAssertion("length_greater_equal", "body.items", 1, "项目数量应该>=1")` |
| `length_less_equal` | 长度小于等于指定值 | `CreateAssertion("length_less_equal", "body.title", 100, "标题长度应该<=100")` |
| `in` | 值在指定列表中 | `CreateAssertion("in", "body.status", []interface{}{"active", "pending"}, "状态应该在允许列表中")` |
| `not_in` | 值不在指定列表中 | `CreateAssertion("not_in", "body.status", []interface{}{"deleted", "banned"}, "状态不应该在禁止列表中")` |

#### type断言支持的数据类型

| 类型值 | 说明 | 示例 |
|--------|------|------|
| `string` | 字符串类型 | `"hello"`, `"123"` |
| `integer` | 整数类型 | `1`, `42`, `-10` |
| `number` | 数字类型（包含小数） | `3.14`, `1.0`, `42` |
| `boolean` | 布尔类型 | `true`, `false` |
| `array` | 数组类型 | `[1, 2, 3]`, `["a", "b"]` |
| `object` | 对象类型 | `{"key": "value"}` |
| `null` | 空值类型 | `null` |

### 配置文件格式

#### JSON格式

```json
{
  "name": "API测试套件",
  "description": "测试描述",
  "tests": [
    {
      "name": "测试用例名称",
      "description": "测试用例描述",
      "request": {
        "method": "GET",
        "url": "https://api.example.com/endpoint",
        "headers": {
          "Authorization": "Bearer {{token}}",
          "Accept": "application/json"
        },
        "params": {
          "page": "1",
          "limit": "10"
        },
        "body": {
          "key": "value"
        }
      },
      "expected": {
        "status_code": 200,
        "headers": {
          "Content-Type": "application/json"
        },
        "assertions": [
          {
            "type": "exists",
            "field": "body.data",
            "message": "响应应该包含data字段"
          },
          {
            "type": "greater_than",
            "field": "body.data.length",
            "value": 0,
            "message": "数据列表不应为空",
            "optional": false
          },
          {
            "type": "not_equals",
            "field": "body.status",
            "value": "error",
            "message": "状态不应该是错误"
          },
          {
            "type": "not_contains",
            "field": "body.message",
            "value": "failed",
            "message": "消息不应该包含失败标识"
          },
          {
            "type": "empty",
            "field": "body.error",
            "message": "错误信息应该为空"
          },
          {
            "type": "length",
            "field": "body.items",
            "value": 10,
            "message": "项目数量应该是10"
          },
          {
            "type": "less_than_or_equal",
            "field": "body.rating",
            "value": 5,
            "message": "评分应该小于等于5（使用别名）"
          }
        ],
        "json_path": {
          "data.length": 10,
          "data.0.id": 1
        }
      },
      "timeout": "30s",
      "retry": 2,
      "variables": {
        "token": "your-api-token"
      }
    }
  ]
}
```

#### YAML格式

```yaml
name: API测试套件
description: 测试描述
tests:
  - name: 测试用例名称
    description: 测试用例描述
    request:
      method: GET
      url: https://api.example.com/endpoint
      headers:
        Authorization: Bearer {{token}}
        Accept: application/json
      params:
        page: "1"
        limit: "10"
      body:
        key: value
    expected:
      status_code: 200
      headers:
        Content-Type: application/json
      assertions:
        - type: exists
          field: body.data
          message: 响应应该包含data字段
        - type: greater_than
          field: body.data.length
          value: 0
          message: 数据列表不应为空
          optional: false
        - type: not_equals
          field: body.status
          value: error
          message: 状态不应该是错误
        - type: not_contains
          field: body.message
          value: failed
          message: 消息不应该包含失败标识
        - type: not_in
          field: body.status
          value: ["deleted", "banned", "suspended"]
          message: 状态不应该在禁止列表中
        - type: length_less_than
          field: body.password
          value: 20
          message: 密码长度应该小于20个字符
        - type: greater_than_or_equal
          field: body.version
          value: 1
          message: 版本号应该大于等于1（使用别名）
      json_path:
        data.length: 10
        data.0.id: 1
    timeout: 30s
    retry: 2
    variables:
      token: your-api-token
```

## 作为命令行工具使用

### 编译

```bash
cd tool/apitesttool
go build -o api-test .
```

### 使用

```bash
# 基本使用
./api-test -config test.json

# 生成HTML报告
./api-test -config test.json -format html -output report.html

# 并发执行
./api-test -config test.json -parallel 5 -verbose

# 使用YAML配置
./api-test -config test.yaml -format html
```

### 命令行参数

- `-config`: 测试配置文件路径（必需）
- `-format`: 报告格式 (console, json, html)
- `-output`: 报告输出路径
- `-parallel`: 并发执行数量
- `-verbose`: 详细输出模式
- `-help`: 显示帮助信息

## 示例

查看以下示例文件了解更多用法：

- `examples/library_usage.go`: 完整的库使用示例
- `examples/simple/main.go`: 简单的库使用示例
- `example_config.json`: JSON配置文件示例
- `simple_test.yaml`: YAML配置文件示例

## 相关文档

- [命令行工具文档](README.md) - 详细的命令行工具使用指南
- [项目总结](SUMMARY.md) - 完整的开发过程和技术总结
- [工具集总览](../README.md) - tool目录下所有工具的总览

## 许可证

本项目遵循公司内部开源协议。 