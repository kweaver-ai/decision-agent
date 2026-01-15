package main

import (
	"fmt"
	"log"
	"os"
	"path/filepath"

	"github.com/kweaver-ai/decision-agent/agent-factory/tool/apitesttool/apitest"
)

func main() {
	fmt.Println("=== API测试配置文件示例 ===\n")

	// 示例1: JSON配置文件
	fmt.Println("1. JSON配置文件示例")
	demonstrateJSONConfig()

	fmt.Println("\n2. YAML配置文件示例")
	demonstrateYAMLConfig()

	fmt.Println("\n3. 复杂配置示例")
	demonstrateComplexConfig()

	fmt.Println("\n4. 环境配置示例")
	demonstrateEnvironmentConfig()
}

// demonstrateJSONConfig 演示JSON配置文件
func demonstrateJSONConfig() {
	// 创建JSON配置文件
	jsonConfig := `{
	"name": "基础API测试套件",
	"description": "演示基础功能的JSON配置",
	"base_url": "https://httpbin.org",
	"timeout": "30s",
	"retry_count": 2,
	"variables": {
		"api_version": "v1",
		"user_agent": "API-Test-Tool/1.0"
	},
	"tests": [
		{
			"name": "健康检查",
			"description": "检查API服务是否正常",
			"request": {
				"method": "GET",
				"url": "{{base_url}}/status/200",
				"headers": {
					"User-Agent": "{{user_agent}}"
				}
			},
			"expected": {
				"status_code": 200,
				"assertions": [
					{
						"type": "exists",
						"field": "headers.Content-Type",
						"message": "应该有Content-Type头"
					}
				]
			}
		},
		{
			"name": "POST数据测试",
			"description": "测试POST请求数据处理",
			"request": {
				"method": "POST",
				"url": "{{base_url}}/post",
				"headers": {
					"Content-Type": "application/json",
					"User-Agent": "{{user_agent}}"
				},
				"body": {
					"username": "${random_string:8}",
					"email": "${random_string:6}@test.com",
					"age": "${random_number:18-65}",
					"created_at": "${timestamp}"
				}
			},
			"expected": {
				"status_code": 200,
				"assertions": [
					{
						"type": "exists",
						"field": "body.json.username",
						"message": "用户名应该存在"
					},
					{
						"type": "contains",
						"field": "body.json.email",
						"value": "@test.com",
						"message": "邮箱应该包含测试域名"
					}
				]
			},
			"variable_extraction": [
				{
					"name": "created_username",
					"source": "body",
					"path": "json.username"
				}
			]
		}
	]
}`

	// 写入临时文件
	tmpFile := filepath.Join(os.TempDir(), "test_config.json")

	err := os.WriteFile(tmpFile, []byte(jsonConfig), 0o644)
	if err != nil {
		log.Printf("写入配置文件失败: %v", err)
		return
	}

	defer os.Remove(tmpFile)

	// 加载并执行测试
	tester := apitest.New()

	config, err := tester.LoadConfigFromFile(tmpFile)
	if err != nil {
		log.Printf("加载JSON配置失败: %v", err)
		return
	}

	report, err := tester.RunTests(config, apitest.WithVerbose(true))
	if err != nil {
		log.Printf("执行测试失败: %v", err)
		return
	}

	fmt.Printf("JSON配置测试结果:\n")
	fmt.Printf("  总测试数: %d\n", report.TotalTests)
	fmt.Printf("  通过数: %d\n", report.PassedTests)
	fmt.Printf("  成功率: %.1f%%\n", report.SuccessRate)
}

// demonstrateYAMLConfig 演示YAML配置文件
func demonstrateYAMLConfig() {
	// 创建YAML配置文件
	yamlConfig := `name: "YAML配置测试套件"
description: "演示YAML格式配置的使用"
base_url: "https://httpbin.org"
timeout: "25s"
retry_count: 1

variables:
  api_key: "test-api-key-123"
  content_type: "application/json"

variable_config:
  random_number_min: 1
  random_number_max: 1000
  random_string_length: 10
  random_name_length: 8

tests:
  - name: "YAML GET测试"
    description: "使用YAML配置的GET请求测试"
    request:
      method: "GET"
      url: "{{base_url}}/get"
      headers:
        Authorization: "Bearer {{api_key}}"
        X-Test-ID: "${uuid}"
      params:
        format: "json"
        timestamp: "${timestamp}"
    expected:
      status_code: 200
      assertions:
        - type: "exists"
          field: "body.args.format"
          message: "format参数应该存在"
        - type: "equals"
          field: "body.args.format"
          value: "json"
          message: "format应该为json"

  - name: "YAML POST测试"
    description: "使用YAML配置的POST请求测试"
    request:
      method: "POST"
      url: "{{base_url}}/post"
      headers:
        Content-Type: "{{content_type}}"
        Authorization: "Bearer {{api_key}}"
      body:
        name: "${random_name}"
        id: "${random_number}"
        token: "${uuid}"
        data:
          nested_field: "${random_string}"
          timestamp: "${timestamp_ms}"
    expected:
      status_code: 200
      assertions:
        - type: "exists"
          field: "body.json.name"
          message: "姓名字段应该存在"
        - type: "exists"
          field: "body.json.data.nested_field"
          message: "嵌套字段应该存在"
    variable_extraction:
      - name: "posted_name"
        source: "body"
        path: "json.name"
      - name: "posted_id"
        source: "body"
        path: "json.id"`

	// 写入临时文件
	tmpFile := filepath.Join(os.TempDir(), "test_config.yaml")

	err := os.WriteFile(tmpFile, []byte(yamlConfig), 0o644)
	if err != nil {
		log.Printf("写入YAML配置文件失败: %v", err)
		return
	}

	defer os.Remove(tmpFile)

	// 加载并执行测试
	tester := apitest.New()

	config, err := tester.LoadConfigFromFile(tmpFile)
	if err != nil {
		log.Printf("加载YAML配置失败: %v", err)
		return
	}

	report, err := tester.RunTests(config, apitest.WithVerbose(true))
	if err != nil {
		log.Printf("执行测试失败: %v", err)
		return
	}

	fmt.Printf("YAML配置测试结果:\n")
	fmt.Printf("  总测试数: %d\n", report.TotalTests)
	fmt.Printf("  通过数: %d\n", report.PassedTests)
	fmt.Printf("  成功率: %.1f%%\n", report.SuccessRate)

	// 显示提取的变量
	fmt.Printf("  提取的变量:\n")

	for name, value := range tester.GetAllVariables() {
		if name == "posted_name" || name == "posted_id" {
			fmt.Printf("    %s = %s\n", name, value)
		}
	}
}

// demonstrateComplexConfig 演示复杂配置
func demonstrateComplexConfig() {
	// 创建复杂的测试配置
	complexConfig := `{
	"name": "复杂API测试场景",
	"description": "演示复杂的测试场景配置",
	"base_url": "https://jsonplaceholder.typicode.com",
	"timeout": "30s",
	"retry_count": 2,
	"parallel": 3,
	
	"variables": {
		"api_base": "https://jsonplaceholder.typicode.com",
		"content_type": "application/json"
	},
	
	"variable_config": {
		"random_number_min": 1,
		"random_number_max": 100,
		"random_string_length": 12,
		"random_name_length": 8
	},
	
	"tests": [
		{
			"name": "创建用户",
			"description": "创建新用户并提取用户ID",
			"request": {
				"method": "POST",
				"url": "{{api_base}}/users",
				"headers": {
					"Content-Type": "{{content_type}}"
				},
				"body": {
					"name": "${random_name}",
					"username": "${random_string:8}",
					"email": "${random_string:6}@example.com",
					"phone": "${random_number:1000000000-9999999999}",
					"website": "https://${random_string:8}.com"
				}
			},
			"expected": {
				"status_code": 201,
				"assertions": [
					{
						"type": "exists",
						"field": "body.id",
						"message": "用户ID应该存在"
					},
					{
						"type": "exists",
						"field": "body.name",
						"message": "用户名应该存在"
					}
				]
			},
			"variable_extraction": [
				{
					"name": "user_id",
					"source": "body",
					"path": "id"
				},
				{
					"name": "user_name",
					"source": "body",
					"path": "name"
				}
			]
		},
		{
			"name": "查询创建的用户",
			"description": "使用提取的用户ID查询用户信息",
			"request": {
				"method": "GET",
				"url": "{{api_base}}/users/{{user_id}}"
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
						"field": "body.name",
						"value": "{{user_name}}",
						"message": "用户名应该匹配"
					}
				]
			}
		},
		{
			"name": "创建用户文章",
			"description": "为用户创建文章",
			"request": {
				"method": "POST",
				"url": "{{api_base}}/posts",
				"headers": {
					"Content-Type": "{{content_type}}"
				},
				"body": {
					"title": "${random_string:20}",
					"body": "${random_string:100}",
					"userId": "{{user_id}}"
				}
			},
			"expected": {
				"status_code": 201,
				"assertions": [
					{
						"type": "exists",
						"field": "body.id",
						"message": "文章ID应该存在"
					},
					{
						"type": "equals",
						"field": "body.userId",
						"value": "{{user_id}}",
						"message": "文章用户ID应该匹配"
					}
				]
			},
			"variable_extraction": [
				{
					"name": "post_id",
					"source": "body",
					"path": "id"
				}
			]
		},
		{
			"name": "获取用户所有文章",
			"description": "获取指定用户的所有文章",
			"request": {
				"method": "GET",
				"url": "{{api_base}}/posts",
				"params": {
					"userId": "{{user_id}}"
				}
			},
			"expected": {
				"status_code": 200,
				"assertions": [
					{
						"type": "exists",
						"field": "body",
						"message": "响应体应该存在"
					}
				]
			}
		}
	]
}`

	// 从字符串加载配置
	tester := apitest.New()

	config, err := tester.LoadConfigFromString(complexConfig, "json")
	if err != nil {
		log.Printf("加载复杂配置失败: %v", err)
		return
	}

	report, err := tester.RunTests(config,
		apitest.WithVerbose(true),
		apitest.WithParallel(2),
	)
	if err != nil {
		log.Printf("执行复杂测试失败: %v", err)
		return
	}

	fmt.Printf("复杂配置测试结果:\n")
	fmt.Printf("  总测试数: %d\n", report.TotalTests)
	fmt.Printf("  通过数: %d\n", report.PassedTests)
	fmt.Printf("  失败数: %d\n", report.FailedTests)
	fmt.Printf("  成功率: %.1f%%\n", report.SuccessRate)
	fmt.Printf("  总耗时: %v\n", report.Duration)

	// 显示所有提取的变量
	fmt.Printf("  提取的变量:\n")

	variables := tester.GetAllVariables()
	for name, value := range variables {
		if name == "user_id" || name == "user_name" || name == "post_id" {
			fmt.Printf("    %s = %s\n", name, value)
		}
	}
}

// demonstrateEnvironmentConfig 演示环境配置
func demonstrateEnvironmentConfig() {
	// 模拟不同环境的测试
	environments := []string{"dev", "staging", "prod"}

	for _, env := range environments {
		fmt.Printf("\n测试环境: %s\n", env)

		// 这里简化处理，实际应该解析JSON并替换current_env

		tester := apitest.New()

		// 手动设置环境变量
		switch env {
		case "dev":
			tester.SetVariables(map[string]string{
				"base_url":    "https://httpbin.org",
				"api_key":     "dev-api-key-123",
				"current_env": "dev",
				"user_agent":  "Multi-Env-Test/1.0",
			})
		case "staging":
			tester.SetVariables(map[string]string{
				"base_url":    "https://httpbin.org",
				"api_key":     "staging-api-key-456",
				"current_env": "staging",
				"user_agent":  "Multi-Env-Test/1.0",
			})
		case "prod":
			tester.SetVariables(map[string]string{
				"base_url":    "https://httpbin.org",
				"api_key":     "prod-api-key-789",
				"current_env": "prod",
				"user_agent":  "Multi-Env-Test/1.0",
			})
		}

		// 执行快速测试
		result := apitest.QuickTest("GET", "{{base_url}}/get",
			apitest.WithHeaders(map[string]string{
				"Authorization": "Bearer {{api_key}}",
				"User-Agent":    "{{user_agent}}",
				"X-Environment": "{{current_env}}",
			}),
			apitest.WithParams(map[string]string{
				"env":       "{{current_env}}",
				"timestamp": "${timestamp}",
			}),
			apitest.WithExpectedStatus(200),
		)

		fmt.Printf("  测试结果: %s\n", getStatusText(result.Success))
		fmt.Printf("  响应时间: %v\n", result.Duration)

		if !result.Success {
			fmt.Printf("  错误: %s\n", result.Error)
		}
	}
}

// getStatusText 获取状态文本
func getStatusText(success bool) string {
	if success {
		return "✅ 成功"
	}

	return "❌ 失败"
}
