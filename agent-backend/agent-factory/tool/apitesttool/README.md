# API测试工具

这是一个用Go语言开发的API自动化测试工具，支持通过JSON或YAML配置文件定义测试用例，并生成详细的测试报告。

## 功能特性

- 🚀 **多种HTTP方法支持**: GET, POST, PUT, DELETE, PATCH等
- 📝 **灵活的配置格式**: 支持JSON和YAML配置文件
- 🔍 **强大的断言系统**: 支持23种断言类型（包含别名），包括JSONPath断言和type类型检查
- 🔄 **重试机制**: 支持失败重试，提高测试稳定性
- ⚡ **并发执行**: 支持并行执行测试用例，提高执行效率
- 📊 **多格式报告**: 支持控制台、JSON、HTML格式的测试报告
- 🔧 **动态变量**: 支持UUID、时间戳、随机数、随机字符串、随机姓名等动态变量
- 🔄 **变量提取**: 支持从API响应中提取变量供后续测试使用
- 🔗 **链式测试**: 支持测试用例间的变量传递和依赖关系
- ⏱️ **超时控制**: 可配置每个测试的超时时间
- 🎯 **可选断言**: 支持可选断言，不影响整体测试结果
- 📚 **双重用途**: 既可作为命令行工具，也可作为Go库使用

## 安装和使用

### 前置要求

- Go 1.23.7 或更高版本

### 编译和运行

1. 进入apitesttool目录：
```bash
cd tool/apitesttool
```

2. 编译程序：
```bash
go build -o api-test .
```

3. 运行测试工具：
```bash
# 使用示例配置文件
./api-test -config example_config.json

# 生成HTML报告
./api-test -config example_config.json -format html -output report.html

# 并行执行测试
./api-test -config example_config.json -parallel 5 -verbose

# 使用YAML配置文件
./api-test -config simple_test.yaml -format html
```

或者直接运行：
```bash
# 使用go run命令
go run . -config example_config.json
go run . -config simple_test.yaml -format html -output report.html
```

### 命令行参数

- `-config`: 测试配置文件路径（必需）
- `-format`: 报告格式，支持 `console`、`json`、`html`（默认：console）
- `-output`: 报告输出路径（可选）
- `-parallel`: 并发执行的测试数量（默认：1）
- `-verbose`: 详细输出模式
- `-help`: 显示帮助信息

## 作为Go库使用

除了命令行工具，本项目还可以作为Go库在其他项目中使用：

```go
import "devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/tool/apitesttool/apitest"

// 快速测试单个API
result := apitest.QuickTest("GET", "https://api.example.com/users",
    apitest.WithExpectedStatus(200),
    apitest.WithAssertions(
        apitest.CreateAssertion("exists", "body.data", nil, "应该包含data字段"),
    ),
)

// 使用配置文件
tester := apitest.New()
config, _ := tester.LoadConfigFromFile("test.json")
report, _ := tester.RunTests(config)
tester.PrintReport(report)
```

详细的库使用文档请参考：[README_LIBRARY.md](README_LIBRARY.md)

## 高级功能

### 动态变量

支持在请求中使用动态生成的变量，每次执行时自动生成新值：

#### 支持的动态变量类型

| 变量类型 | 语法 | 说明 | 示例值 |
|---------|------|------|--------|
| UUID | `${uuid}` | 生成UUID | `550e8400-e29b-41d4-a716-446655440000` |
| 时间戳 | `${timestamp}` | Unix时间戳（秒） | `1640995200` |
| 毫秒时间戳 | `${timestamp_ms}` | Unix时间戳（毫秒） | `1640995200000` |
| 随机数 | `${random_number}` | 默认范围随机数 | `42` |
| 自定义范围随机数 | `${random_number:min-max}` | 指定范围随机数 | `${random_number:1-100}` |
| 随机字符串 | `${random_string}` | 默认长度随机字符串 | `aBc123XyZ` |
| 自定义长度随机字符串 | `${random_string:length}` | 指定长度随机字符串 | `${random_string:12}` |
| 随机姓名 | `${random_name}` | 默认长度随机姓名 | `JohnSmith` |
| 自定义长度随机姓名 | `${random_name:length}` | 指定长度随机姓名 | `${random_name:10}` |

#### 动态变量使用示例

```json
{
  "name": "动态变量测试",
  "variable_config": {
    "random_number_min": 1,
    "random_number_max": 1000,
    "random_string_length": 12,
    "random_name_length": 8
  },
  "tests": [
    {
      "name": "创建用户",
      "request": {
        "method": "POST",
        "url": "https://api.example.com/users",
        "headers": {
          "Content-Type": "application/json",
          "X-Request-ID": "${uuid}",
          "X-Timestamp": "${timestamp}"
        },
        "body": {
          "username": "${random_string:10}",
          "email": "${random_string:6}@example.com",
          "age": "${random_number:18-65}",
          "phone": "${random_number:1000000000-9999999999}",
          "display_name": "${random_name:12}",
          "created_at": "${timestamp_ms}"
        }
      },
      "expected": {
        "status_code": 201
      }
    }
  ]
}
```

### 变量提取

从API响应中提取数据并保存为变量，供后续测试使用：

#### 变量提取配置

```json
{
  "variable_extraction": [
    {
      "name": "user_id",           // 变量名
      "source": "body",            // 提取源: body, header, status_code
      "path": "id"                 // JSONPath或字段路径
    },
    {
      "name": "auth_token",
      "source": "header",
      "path": "Authorization"
    },
    {
      "name": "email_domain",
      "source": "body",
      "path": "email",
      "regex": "@(.+)$"            // 正则表达式提取
    }
  ]
}
```

#### 变量提取示例

```json
{
  "name": "变量提取示例",
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
      "expected": {
        "status_code": 201
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
      "name": "步骤2: 查询创建的资源",
      "request": {
        "method": "GET",
        "url": "https://api.example.com/resources/{{resource_id}}"
      },
      "expected": {
        "status_code": 200,
        "assertions": [
          {
            "type": "equals",
            "field": "body.id",
            "value": "{{resource_id}}",
            "message": "资源ID应该匹配"
          }
        ]
      }
    }
  ]
}
```

### 链式测试

通过变量提取和传递实现测试用例间的依赖关系：

```json
{
  "name": "用户管理链式测试",
  "variables": {
    "base_url": "https://api.example.com",
    "api_key": "your-api-key"
  },
  "tests": [
    {
      "name": "步骤1: 创建用户",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/users",
        "headers": {
          "Authorization": "Bearer {{api_key}}",
          "Content-Type": "application/json"
        },
        "body": {
          "username": "${random_string:8}",
          "email": "${random_string:6}@test.com",
          "password": "${random_string:12}"
        }
      },
      "expected": {
        "status_code": 201
      },
      "variable_extraction": [
        {
          "name": "user_id",
          "source": "body",
          "path": "id"
        },
        {
          "name": "username",
          "source": "body",
          "path": "username"
        }
      ]
    },
    {
      "name": "步骤2: 获取用户信息",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/users/{{user_id}}",
        "headers": {
          "Authorization": "Bearer {{api_key}}"
        }
      },
      "expected": {
        "status_code": 200,
        "assertions": [
          {
            "type": "equals",
            "field": "body.id",
            "value": "{{user_id}}",
            "message": "用户ID应该匹配"
          },
          {
            "type": "equals",
            "field": "body.username",
            "value": "{{username}}",
            "message": "用户名应该匹配"
          }
        ]
      }
    },
    {
      "name": "步骤3: 更新用户信息",
      "request": {
        "method": "PUT",
        "url": "{{base_url}}/users/{{user_id}}",
        "headers": {
          "Authorization": "Bearer {{api_key}}",
          "Content-Type": "application/json"
        },
        "body": {
          "username": "{{username}}_updated",
          "email": "updated_${random_string:6}@test.com"
        }
      },
      "expected": {
        "status_code": 200
      },
      "variable_extraction": [
        {
          "name": "updated_email",
          "source": "body",
          "path": "email"
        }
      ]
    },
    {
      "name": "步骤4: 验证更新结果",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/users/{{user_id}}",
        "headers": {
          "Authorization": "Bearer {{api_key}}"
        }
      },
      "expected": {
        "status_code": 200,
        "assertions": [
          {
            "type": "equals",
            "field": "body.username",
            "value": "{{username}}_updated",
            "message": "用户名应该已更新"
          },
          {
            "type": "equals",
            "field": "body.email",
            "value": "{{updated_email}}",
            "message": "邮箱应该已更新"
          }
        ]
      }
    },
    {
      "name": "步骤5: 删除用户",
      "request": {
        "method": "DELETE",
        "url": "{{base_url}}/users/{{user_id}}",
        "headers": {
          "Authorization": "Bearer {{api_key}}"
        }
      },
      "expected": {
        "status_code": 204
      }
    }
  ]
}
```

## 配置文件格式

### JSON格式示例

```json
{
  "name": "API测试套件",
  "description": "测试套件描述",
  "variables": {
    "base_url": "https://api.example.com",
    "api_key": "your-api-key"
  },
  "variable_config": {
    "random_number_min": 1,
    "random_number_max": 1000,
    "random_string_length": 12,
    "random_name_length": 8
  },
  "tests": [
    {
      "name": "测试用例名称",
      "description": "测试用例描述",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/users",
        "headers": {
          "Accept": "application/json",
          "Authorization": "Bearer {{api_key}}",
          "X-Request-ID": "${uuid}"
        },
        "params": {
          "page": "1",
          "limit": "${random_number:1-50}"
        },
        "body": {
          "username": "${random_string:10}",
          "email": "${random_string:6}@test.com"
        }
      },
      "expected": {
        "status_code": 200,
        "headers": {
          "Content-Type": "application/json"
        },
        "json_path": {
          "data.0.id": 1,
          "data.length": 10
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
            "message": "数据列表不应为空"
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
            "type": "starts_with",
            "field": "body.username",
            "value": "user_",
            "message": "用户名应该以user_开头"
          },
          {
            "type": "length_greater_than",
            "field": "body.data",
            "value": 0,
            "message": "数据列表长度应该大于0"
          },
          {
            "type": "in",
            "field": "body.status",
            "value": ["active", "pending", "completed"],
            "message": "状态应该在允许的值中"
          },
          {
            "type": "greater_than_or_equal",
            "field": "body.score",
            "value": 0,
            "message": "分数应该大于等于0（使用别名）"
          }
        ]
      },
      "variable_extraction": [
        {
          "name": "first_user_id",
          "source": "body",
          "path": "data.0.id"
        },
        {
          "name": "total_count",
          "source": "body",
          "path": "data.length"
        }
      ],
      "timeout": "30s",
      "retry": 2
    }
  ]
}
```

### YAML格式示例

```yaml
name: API测试套件
description: 测试套件描述
variables:
  base_url: https://api.example.com
  api_key: your-api-key

variable_config:
  random_number_min: 1
  random_number_max: 1000
  random_string_length: 12
  random_name_length: 8

tests:
  - name: 测试用例名称
    description: 测试用例描述
    request:
      method: GET
      url: "{{base_url}}/users"
      headers:
        Accept: application/json
        Authorization: "Bearer {{api_key}}"
        X-Request-ID: "${uuid}"
      params:
        page: "1"
        limit: "${random_number:1-50}"
    expected:
      status_code: 200
      assertions:
        - type: exists
          field: body.data
          message: 响应应该包含data字段
        - type: not_equals
          field: body.status
          value: error
          message: 状态不应该是错误
        - type: not_contains
          field: body.message
          value: failed
          message: 消息不应该包含失败标识
        - type: ends_with
          field: body.email
          value: "@example.com"
          message: 邮箱应该以@example.com结尾
        - type: not_empty
          field: body.data
          message: 数据不应该为空
        - type: length_less_equal
          field: body.title
          value: 100
          message: 标题长度不应该超过100个字符
        - type: less_than_or_equal
          field: body.priority
          value: 10
          message: 优先级应该小于等于10（使用别名）
    variable_extraction:
      - name: first_user_id
        source: body
        path: data.0.id
    timeout: 30s
    retry: 2
```

## 配置字段说明

### 测试配置 (TestConfig)

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| name | string | 是 | 测试套件名称 |
| description | string | 否 | 测试套件描述 |
| variables | map[string]string | 否 | 全局变量定义 |
| variable_config | VariableConfig | 否 | 动态变量配置 |
| tests | []APITest | 是 | 测试用例列表 |

### 变量配置 (VariableConfig)

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| random_number_min | int | 否 | 随机数最小值（默认：1） |
| random_number_max | int | 否 | 随机数最大值（默认：1000） |
| random_string_length | int | 否 | 随机字符串默认长度（默认：10） |
| random_name_length | int | 否 | 随机姓名默认长度（默认：8） |

### 测试用例 (APITest)

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| name | string | 否 | 测试用例名称 |
| description | string | 否 | 测试用例描述 |
| request | RequestConfig | 是 | 请求配置 |
| expected | ExpectedResponse | 否 | 期望响应 |
| variable_extraction | []VariableExtraction | 否 | 变量提取配置 |
| timeout | duration | 否 | 超时时间（如：30s, 5m） |
| retry | int | 否 | 重试次数 |
| variables | map[string]string | 否 | 局部变量定义 |

### 请求配置 (RequestConfig)

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| method | string | 否 | HTTP方法（默认：GET） |
| url | string | 否* | 完整URL |
| host | string | 否* | 主机地址 |
| path | string | 否* | 请求路径 |
| headers | map[string]string | 否 | 请求头 |
| params | map[string]string | 否 | URL参数 |
| body | interface{} | 否 | 请求体 |

*注：url 和 host+path 二选一

### 期望响应 (ExpectedResponse)

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| status_code | int | 否 | 期望状态码 |
| headers | map[string]string | 否 | 期望响应头 |
| body | interface{} | 否 | 期望响应体 |
| json_path | map[string]interface{} | 否 | JSONPath断言 |
| assertions | []AssertionConfig | 否 | 自定义断言 |

### 变量提取配置 (VariableExtraction)

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| name | string | 是 | 变量名 |
| source | string | 是 | 提取源：body, header, status_code |
| path | string | 是 | JSONPath或字段路径 |
| regex | string | 否 | 正则表达式提取 |
| default | string | 否 | 默认值 |

### 断言配置 (AssertionConfig)

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| type | string | 是 | 断言类型 |
| field | string | 是 | 断言字段路径 |
| value | interface{} | 否 | 期望值 |
| message | string | 否 | 断言失败消息 |
| optional | bool | 否 | 是否为可选断言 |

## 断言类型

| 类型 | 说明 | 示例 |
|------|------|------|
| equals | 值相等 | `{"type": "equals", "field": "body.id", "value": 1}` |
| not_equals | 值不相等 | `{"type": "not_equals", "field": "body.status", "value": "error"}` |
| contains | 包含字符串 | `{"type": "contains", "field": "body.name", "value": "test"}` |
| not_contains | 不包含字符串 | `{"type": "not_contains", "field": "body.message", "value": "error"}` |
| regex | 正则表达式匹配 | `{"type": "regex", "field": "body.email", "value": "^[\\w-\\.]+@([\\w-]+\\.)+[\\w-]{2,4}$"}` |
| exists | 字段存在 | `{"type": "exists", "field": "body.data"}` |
| not_exists | 字段不存在 | `{"type": "not_exists", "field": "body.error"}` |
| greater_than | 大于 | `{"type": "greater_than", "field": "body.count", "value": 0}` |
| less_than | 小于 | `{"type": "less_than", "field": "body.count", "value": 100}` |
| greater_equal | 大于等于 | `{"type": "greater_equal", "field": "body.score", "value": 60}` |
| greater_than_or_equal | 大于等于（别名） | `{"type": "greater_than_or_equal", "field": "body.score", "value": 60}` |
| less_equal | 小于等于 | `{"type": "less_equal", "field": "body.score", "value": 100}` |
| less_than_or_equal | 小于等于（别名） | `{"type": "less_than_or_equal", "field": "body.score", "value": 100}` |
| type | 类型检查 | `{"type": "type", "field": "body.id", "value": "string"}` |
| starts_with | 字符串以指定内容开头 | `{"type": "starts_with", "field": "body.name", "value": "user_"}` |
| ends_with | 字符串以指定内容结尾 | `{"type": "ends_with", "field": "body.email", "value": "@example.com"}` |
| empty | 值为空 | `{"type": "empty", "field": "body.description"}` |
| not_empty | 值不为空 | `{"type": "not_empty", "field": "body.data"}` |
| length | 长度等于指定值 | `{"type": "length", "field": "body.items", "value": 5}` |
| length_greater_than | 长度大于指定值 | `{"type": "length_greater_than", "field": "body.list", "value": 0}` |
| length_less_than | 长度小于指定值 | `{"type": "length_less_than", "field": "body.name", "value": 50}` |
| length_greater_equal | 长度大于等于指定值 | `{"type": "length_greater_equal", "field": "body.items", "value": 1}` |
| length_less_equal | 长度小于等于指定值 | `{"type": "length_less_equal", "field": "body.title", "value": 100}` |
| in | 值在指定列表中 | `{"type": "in", "field": "body.status", "value": ["active", "pending"]}` |
| not_in | 值不在指定列表中 | `{"type": "not_in", "field": "body.status", "value": ["deleted", "banned"]}` |

### 断言类型详细说明

#### 字符串断言
- **`starts_with`**: 检查字符串是否以指定内容开头
- **`ends_with`**: 检查字符串是否以指定内容结尾
- **`contains`**: 检查字符串是否包含指定内容
- **`not_contains`**: 检查字符串是否不包含指定内容

#### 长度断言
- **`length`**: 检查值的长度是否等于指定值（支持字符串、数组、对象）
- **`length_greater_than`**: 检查长度是否大于指定值
- **`length_less_than`**: 检查长度是否小于指定值
- **`length_greater_equal`**: 检查长度是否大于等于指定值
- **`length_less_equal`**: 检查长度是否小于等于指定值

#### 空值断言
- **`empty`**: 检查值是否为空（空字符串、空数组、空对象、0、false、null）
- **`not_empty`**: 检查值是否不为空

#### 列表断言
- **`in`**: 检查值是否在指定列表中
- **`not_in`**: 检查值是否不在指定列表中

#### 数值比较断言
- **`greater_than`**: 大于比较
- **`less_than`**: 小于比较
- **`greater_equal`** / **`greater_than_or_equal`**: 大于等于比较（支持两种写法）
- **`less_equal`** / **`less_than_or_equal`**: 小于等于比较（支持两种写法）

#### 相等性断言
- **`equals`**: 值相等
- **`not_equals`**: 值不相等

#### 存在性断言
- **`exists`**: 字段存在
- **`not_exists`**: 字段不存在

#### 类型断言
- **`type`**: 检查值的数据类型

### 断言别名支持

为了提高可读性和兼容性，部分断言类型支持多种写法：

| 标准名称 | 别名 | 说明 |
|---------|------|------|
| `greater_equal` | `greater_than_or_equal` | 大于等于断言的两种写法 |
| `less_equal` | `less_than_or_equal` | 小于等于断言的两种写法 |

这些别名在功能上完全相同，您可以根据个人喜好或团队规范选择使用。

### type断言支持的数据类型

| 类型值 | 说明 | 示例 |
|--------|------|------|
| `string` | 字符串类型 | `"hello"`, `"123"` |
| `integer` | 整数类型 | `1`, `42`, `-10` |
| `number` | 数字类型（包含小数） | `3.14`, `1.0`, `42` |
| `boolean` | 布尔类型 | `true`, `false` |
| `array` | 数组类型 | `[1, 2, 3]`, `["a", "b"]` |
| `object` | 对象类型 | `{"key": "value"}` |
| `null` | 空值类型 | `null` |

## 字段路径说明

- `status_code`: HTTP状态码
- `headers.Header-Name`: 响应头字段
- `body`: 完整响应体
- `body.field`: JSON响应体中的字段（支持嵌套，如：`body.data.0.id`）

## 变量替换

支持两种变量语法：

### 1. 用户定义变量
使用 `{{variable_name}}` 格式引用用户定义的变量：

```json
{
  "variables": {
    "user_id": "123",
    "api_key": "your-api-token"
  },
  "request": {
    "url": "https://api.example.com/users/{{user_id}}",
    "headers": {
      "Authorization": "Bearer {{api_key}}"
    }
  }
}
```

### 2. 动态变量
使用 `${variable_type}` 格式引用动态生成的变量：

```json
{
  "request": {
    "headers": {
      "X-Request-ID": "${uuid}",
      "X-Timestamp": "${timestamp}"
    },
    "body": {
      "username": "${random_string:8}",
      "age": "${random_number:18-65}"
    }
  }
}
```

## 报告格式

### 控制台报告
直接在终端输出测试结果，适合快速查看。

### JSON报告
生成结构化的JSON报告文件，适合程序化处理。

### HTML报告
生成美观的HTML报告，包含详细的测试信息和统计图表，支持折叠展开功能，适合分享和存档。HTML报告特性：
- 📊 **统计概览**：总测试数、通过/失败数、成功率、总耗时
- 🎨 **美观界面**：现代化设计，响应式布局
- 📱 **移动友好**：支持手机和平板设备查看
- 🔍 **详细信息**：请求/响应详情、断言结果、变量信息
- 📋 **折叠功能**：默认折叠，点击展开详情
- ⏱️ **精确计时**：显示精确到毫秒的执行时间

## 示例文件

项目包含以下示例文件：

- **`example_config.json`**: 完整的JSON配置示例，包含8个不同类型的测试用例
- **`simple_test.yaml`**: 简单的YAML配置示例，包含基础的GET和POST测试
- **`examples/`**: 完整的使用示例目录
  - `basic_usage.go`: 基础使用示例
  - `advanced/main.go`: 高级功能示例（动态变量、变量提取、链式测试）
  - `performance/main.go`: 性能测试示例
  - `config/main.go`: 配置文件示例
  - `errors/main.go`: 错误处理示例
  - `README.md`: 详细的示例说明文档

## 项目结构

```
apitesttool/
├── main.go                 # 命令行工具入口
├── apitest/                # 核心功能包
│   ├── config.go           # 配置结构定义
│   ├── executor.go         # 测试执行器
│   ├── reporter.go         # 报告生成器
│   ├── variables.go        # 变量管理器
│   └── apitest.go          # 库接口
├── examples/               # 使用示例
│   ├── basic_usage.go      # 基础使用示例
│   ├── advanced/           # 高级功能示例
│   ├── performance/        # 性能测试示例
│   ├── config/             # 配置文件示例
│   ├── errors/             # 错误处理示例
│   └── README.md           # 示例说明文档
├── example_config.json     # JSON配置示例
├── simple_test.yaml        # YAML配置示例
├── README.md               # 本文档
└── README_LIBRARY.md       # 库使用详细文档
```

## 开发和扩展

如需扩展功能，可以：

1. **添加新的断言类型**：在 `apitest/executor.go` 中的 `performAssertion` 方法中添加新的断言逻辑
2. **添加新的报告格式**：在 `apitest/reporter.go` 中实现新的报告生成方法
3. **扩展配置选项**：在 `apitest/config.go` 中添加新的配置字段
4. **添加新的HTTP功能**：在 `apitest/executor.go` 中扩展HTTP请求处理逻辑
5. **添加新的动态变量类型**：在 `apitest/variables.go` 中扩展动态变量生成逻辑

## 相关文档

- [库使用文档](README_LIBRARY.md) - 详细的Go库使用指南和高级功能说明
- [示例文档](examples/README.md) - 完整的使用示例和说明
- [工具集总览](../README.md) - tool目录下所有工具的总览

## 许可证

本项目遵循公司内部开源协议。 