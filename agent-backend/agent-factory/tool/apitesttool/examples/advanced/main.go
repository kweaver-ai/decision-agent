package main

import (
	"fmt"
	"log"
	"time"

	"github.com/kweaver-ai/decision-agent/agent-factory/tool/apitesttool/apitest"
)

func main() {
	fmt.Println("=== API测试工具高级功能示例 ===\n")

	// 示例1: 动态变量使用
	fmt.Println("1. 动态变量使用演示")
	demonstrateDynamicVariables()

	fmt.Println("\n2. 变量提取功能演示")
	demonstrateVariableExtraction()

	fmt.Println("\n3. 链式测试演示")
	demonstrateChainedTests()

	fmt.Println("\n4. 变量管理器直接使用")
	demonstrateVariableManager()
}

// demonstrateDynamicVariables 演示动态变量的使用
func demonstrateDynamicVariables() {
	// 使用各种动态变量进行快速测试
	result := apitest.QuickTest("POST", "https://httpbin.org/post",
		apitest.WithHeaders(map[string]string{
			"Content-Type": "application/json",
			"X-Request-ID": "${uuid}",
			"X-Timestamp":  "${timestamp}",
			"X-Random-Num": "${random_number:1-100}",
			"X-Random-Str": "${random_string:8}",
		}),
		apitest.WithBody(map[string]interface{}{
			"user_id":      "${random_number:1000-9999}",
			"username":     "${random_string:10}",
			"display_name": "${random_name:8}",
			"email":        "${random_string:6}@example.com",
			"created_at":   "${timestamp_ms}",
			"session_id":   "${uuid}",
		}),
		apitest.WithTimeout(30*time.Second),
	)

	fmt.Printf("测试结果: %s\n", getStatusText(result.Success))
	fmt.Printf("响应时间: %v\n", result.Duration.Round(time.Millisecond))

	if result.Success {
		fmt.Println("✅ 动态变量替换成功")
		// 显示一些请求信息
		fmt.Printf("请求URL: %s\n", result.Request.URL)
		fmt.Printf("请求头数量: %d\n", len(result.Request.Headers))

		// 显示生成的动态变量值
		fmt.Println("生成的动态变量值:")

		for key, value := range result.Request.Headers {
			if key == "X-Request-ID" || key == "X-Timestamp" || key == "X-Random-Num" || key == "X-Random-Str" {
				fmt.Printf("  %s: %s\n", key, value)
			}
		}
	} else {
		fmt.Printf("❌ 测试失败: %s\n", result.Error)
	}
}

// demonstrateVariableExtraction 演示变量提取功能
func demonstrateVariableExtraction() {
	tester := apitest.New()

	// 第一步：创建一个资源并提取ID
	fmt.Println("步骤1: 创建资源并提取变量")

	createTest := apitest.APITest{
		Name: "创建用户",
		Request: apitest.RequestConfig{
			Method: "POST",
			URL:    "https://jsonplaceholder.typicode.com/users",
			Headers: map[string]string{
				"Content-Type": "application/json",
			},
			Body: map[string]interface{}{
				"name":     "${random_name:6}",
				"username": "${random_string:8}",
				"email":    "${random_string:5}@test.com",
			},
		},
		Expected: apitest.ExpectedResponse{
			StatusCode: 201,
		},
		VariableExtraction: []apitest.VariableExtraction{
			{
				Name:   "created_user_id",
				Source: "body",
				Path:   "id",
			},
			{
				Name:   "created_user_name",
				Source: "body",
				Path:   "name",
			},
		},
		Timeout: apitest.Duration(30 * time.Second),
	}

	result1 := tester.RunSingleTest(createTest)
	fmt.Printf("创建用户结果: %s\n", getStatusText(result1.Success))

	if result1.Success {
		fmt.Println("✅ 变量提取成功")

		for name, value := range result1.Variables {
			fmt.Printf("  %s = %s\n", name, value)
		}
	}

	// 第二步：使用提取的变量
	fmt.Println("\n步骤2: 使用提取的变量查询用户")

	if userID, exists := tester.GetVariable("created_user_id"); exists {
		queryTest := apitest.APITest{
			Name: "查询创建的用户",
			Request: apitest.RequestConfig{
				Method: "GET",
				URL:    fmt.Sprintf("https://jsonplaceholder.typicode.com/users/%s", userID),
			},
			Expected: apitest.ExpectedResponse{
				StatusCode: 200,
				Assertions: []apitest.AssertionConfig{
					{
						Type:    "exists",
						Field:   "body.id",
						Message: "用户ID应该存在",
					},
				},
			},
		}

		result2 := tester.RunSingleTest(queryTest)
		fmt.Printf("查询用户结果: %s\n", getStatusText(result2.Success))

		if result2.Success {
			fmt.Println("✅ 使用提取的变量成功")
		}
	}
}

// demonstrateChainedTests 演示链式测试
func demonstrateChainedTests() {
	tester := apitest.New()

	// 设置全局变量
	tester.SetVariables(map[string]string{
		"base_url": "https://httpbin.org",
		"api_key":  "test-api-key-123",
	})

	// 创建链式测试配置
	configData := `{
		"name": "链式测试演示",
		"description": "演示变量在测试间的传递",
		"variables": {
			"base_url": "https://httpbin.org"
		},
		"tests": [
			{
				"name": "步骤1: 生成会话",
				"request": {
					"method": "POST",
					"url": "{{base_url}}/post",
					"headers": {
						"Content-Type": "application/json"
					},
					"body": {
						"session_id": "${uuid}",
						"user_id": "${random_number:1000-9999}",
						"timestamp": "${timestamp}"
					}
				},
				"expected": {
					"status_code": 200
				},
				"variable_extraction": [
					{
						"name": "session_id",
						"source": "body",
						"path": "json.session_id"
					},
					{
						"name": "user_id",
						"source": "body",
						"path": "json.user_id"
					}
				]
			},
			{
				"name": "步骤2: 使用会话信息",
				"request": {
					"method": "GET",
					"url": "{{base_url}}/get",
					"params": {
						"session_id": "{{session_id}}",
						"user_id": "{{user_id}}"
					}
				},
				"expected": {
					"status_code": 200,
					"assertions": [
						{
							"type": "equals",
							"field": "body.args.session_id",
							"value": "{{session_id}}",
							"message": "会话ID应该匹配"
						}
					]
				}
			}
		]
	}`

	config, err := tester.LoadConfigFromString(configData, "json")
	if err != nil {
		log.Printf("加载配置失败: %v", err)
		return
	}

	report, err := tester.RunTests(config, apitest.WithVerbose(true))
	if err != nil {
		log.Printf("执行测试失败: %v", err)
		return
	}

	fmt.Printf("\n链式测试结果:\n")
	fmt.Printf("总测试数: %d\n", report.TotalTests)
	fmt.Printf("通过数: %d\n", report.PassedTests)
	fmt.Printf("成功率: %.1f%%\n", report.SuccessRate)

	// 显示最终变量状态
	fmt.Printf("\n最终变量状态:\n")

	variables := tester.GetAllVariables()
	for name, value := range variables {
		fmt.Printf("  %s = %s\n", name, value)
	}
}

// demonstrateVariableManager 演示变量管理器的直接使用
func demonstrateVariableManager() {
	// 创建自定义变量配置
	config := apitest.VariableConfig{
		RandomNumberMin:    100,
		RandomNumberMax:    999,
		RandomStringLength: 12,
		RandomNameLength:   10,
	}

	vm := apitest.NewVariableManagerWithConfig(config)

	// 设置一些变量
	vm.SetVariables(map[string]string{
		"api_base":    "https://httpbin.org",
		"api_version": "v1",
		"user_agent":  "API-Test-Tool/1.0",
	})

	fmt.Println("设置的变量:")

	for name, value := range vm.GetAllVariables() {
		fmt.Printf("  %s = %s\n", name, value)
	}

	// 测试动态变量生成
	fmt.Println("\n动态变量生成测试:")

	testStrings := []string{
		"UUID: ${uuid}",
		"时间戳: ${timestamp}",
		"毫秒时间戳: ${timestamp_ms}",
		"随机数: ${random_number}",
		"自定义范围随机数: ${random_number:500-600}",
		"随机字符串: ${random_string}",
		"自定义长度随机字符串: ${random_string:15}",
		"随机姓名: ${random_name}",
		"自定义长度随机姓名: ${random_name:12}",
	}

	for _, testStr := range testStrings {
		result := vm.ReplaceVariables(testStr)
		fmt.Printf("  %s\n", result)
	}

	// 测试变量提取
	fmt.Println("\n变量提取测试:")

	// 模拟响应数据
	response := apitest.ResponseInfo{
		StatusCode: 200,
		Headers: map[string]string{
			"Content-Type": "application/json",
			"X-Request-ID": "req-12345",
		},
		Body: `{"id": 42, "name": "测试用户", "email": "test@example.com", "status": "active"}`,
	}

	extractions := []apitest.VariableExtraction{
		{Name: "extracted_id", Source: "body", Path: "id"},
		{Name: "extracted_name", Source: "body", Path: "name"},
		{Name: "extracted_email", Source: "body", Path: "email"},
		{Name: "request_id", Source: "header", Path: "X-Request-ID"},
		{Name: "email_domain", Source: "body", Path: "email", Regex: "@(.+)$"},
	}

	err := vm.ExtractVariables(extractions, response)
	if err != nil {
		fmt.Printf("❌ 变量提取失败: %v\n", err)
	} else {
		fmt.Println("✅ 变量提取成功:")

		for name, value := range vm.GetAllVariables() {
			fmt.Printf("  %s = %s\n", name, value)
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
