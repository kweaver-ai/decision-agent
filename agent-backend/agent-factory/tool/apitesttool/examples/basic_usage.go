package main

import (
	"fmt"
	"log"
	"time"

	"github.com/kweaver-ai/decision-agent/agent-factory/tool/apitesttool/apitest"
)

func main() {
	fmt.Println("=== API测试工具基础使用示例 ===\n")

	// 示例1: 最简单的GET请求测试
	fmt.Println("1. 简单GET请求测试")
	simpleGetTest()

	fmt.Println("\n2. POST请求测试")
	simplePostTest()

	fmt.Println("\n3. 带断言的测试")
	testWithAssertions()

	fmt.Println("\n4. 从配置文件加载测试")
	testFromConfig()
}

// simpleGetTest 最简单的GET请求测试
func simpleGetTest() {
	result := apitest.QuickTest("GET", "https://httpbin.org/get")

	fmt.Printf("测试结果: %s\n", getStatusText(result.Success))
	fmt.Printf("响应时间: %v\n", result.Duration.Round(time.Millisecond))
	fmt.Printf("状态码: %d\n", result.Response.StatusCode)

	if !result.Success {
		fmt.Printf("错误: %s\n", result.Error)
	}
}

// simplePostTest POST请求测试
func simplePostTest() {
	result := apitest.QuickTest("POST", "https://httpbin.org/post",
		apitest.WithHeaders(map[string]string{
			"Content-Type": "application/json",
		}),
		apitest.WithBody(map[string]interface{}{
			"name":    "测试用户",
			"email":   "test@example.com",
			"message": "这是一个测试消息",
		}),
		apitest.WithTimeout(30*time.Second),
	)

	fmt.Printf("测试结果: %s\n", getStatusText(result.Success))
	fmt.Printf("响应时间: %v\n", result.Duration.Round(time.Millisecond))
	fmt.Printf("响应大小: %d bytes\n", result.Response.Size)
}

// testWithAssertions 带断言的测试
func testWithAssertions() {
	result := apitest.QuickTest("GET", "https://httpbin.org/json",
		apitest.WithExpectedStatus(200),
		apitest.WithAssertions(
			apitest.CreateAssertion("exists", "body.slideshow", nil, "slideshow字段应该存在"),
			apitest.CreateAssertion("exists", "body.slideshow.title", nil, "title字段应该存在"),
			apitest.CreateAssertion("equals", "body.slideshow.author", "Yours Truly", "作者应该匹配"),
		),
	)

	fmt.Printf("测试结果: %s\n", getStatusText(result.Success))
	fmt.Printf("断言数量: %d\n", len(result.Assertions))

	for i, assertion := range result.Assertions {
		status := "✓"
		if !assertion.Success {
			status = "✗"
		}

		fmt.Printf("  断言%d %s: %s\n", i+1, status, assertion.Message)
	}
}

// testFromConfig 从配置文件加载测试
func testFromConfig() {
	// 创建测试器
	tester := apitest.New()

	// 创建简单的配置
	configData := `{
		"name": "基础API测试",
		"description": "演示基础功能的测试套件",
		"tests": [
			{
				"name": "获取IP信息",
				"request": {
					"method": "GET",
					"url": "https://httpbin.org/ip"
				},
				"expected": {
					"status_code": 200,
					"assertions": [
						{
							"type": "exists",
							"field": "body.origin",
							"message": "应该返回IP地址"
						}
					]
				}
			},
			{
				"name": "测试User-Agent",
				"request": {
					"method": "GET",
					"url": "https://httpbin.org/user-agent",
					"headers": {
						"User-Agent": "API-Test-Tool/1.0"
					}
				},
				"expected": {
					"status_code": 200,
					"assertions": [
						{
							"type": "contains",
							"field": "body.user-agent",
							"value": "API-Test-Tool",
							"message": "User-Agent应该包含工具名称"
						}
					]
				}
			}
		]
	}`

	// 从字符串加载配置
	config, err := tester.LoadConfigFromString(configData, "json")
	if err != nil {
		log.Printf("加载配置失败: %v", err)
		return
	}

	// 执行测试
	report, err := tester.RunTests(config, apitest.WithVerbose(true))
	if err != nil {
		log.Printf("执行测试失败: %v", err)
		return
	}

	// 打印报告
	fmt.Printf("\n测试报告:\n")
	fmt.Printf("总测试数: %d\n", report.TotalTests)
	fmt.Printf("通过数: %d\n", report.PassedTests)
	fmt.Printf("失败数: %d\n", report.FailedTests)
	fmt.Printf("成功率: %.1f%%\n", report.SuccessRate)
}

// getStatusText 获取状态文本
func getStatusText(success bool) string {
	if success {
		return "✅ 成功"
	}

	return "❌ 失败"
}
