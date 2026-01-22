package main

import (
	"fmt"
	"time"

	"github.com/kweaver-ai/decision-agent/agent-factory/tool/apitesttool/apitest"
)

func main() {
	fmt.Println("=== API测试错误处理示例 ===\n")

	// 示例1: 网络错误处理
	fmt.Println("1. 网络错误处理")
	demonstrateNetworkErrors()

	fmt.Println("\n2. 超时错误处理")
	demonstrateTimeoutErrors()

	fmt.Println("\n3. 状态码错误处理")
	demonstrateStatusCodeErrors()

	fmt.Println("\n4. 断言失败处理")
	demonstrateAssertionErrors()
}

// demonstrateNetworkErrors 演示网络错误处理
func demonstrateNetworkErrors() {
	fmt.Println("测试无效URL的网络错误:")

	// 测试无效的URL
	result := apitest.QuickTest("GET", "http://invalid-domain-that-does-not-exist.com/api",
		apitest.WithTimeout(5*time.Second),
	)

	fmt.Printf("  测试结果: %s\n", getStatusText(result.Success))

	if !result.Success {
		fmt.Printf("  错误信息: %s\n", result.Error)
		fmt.Printf("  错误类型: 网络连接失败\n")
	}
}

// demonstrateTimeoutErrors 演示超时错误处理
func demonstrateTimeoutErrors() {
	fmt.Println("测试请求超时:")

	// 设置很短的超时时间，测试长延迟的请求
	result := apitest.QuickTest("GET", "https://httpbin.org/delay/10",
		apitest.WithTimeout(2*time.Second), // 2秒超时，但服务器需要10秒
	)

	fmt.Printf("  测试结果: %s\n", getStatusText(result.Success))
	fmt.Printf("  响应时间: %v\n", result.Duration.Round(time.Millisecond))

	if !result.Success {
		fmt.Printf("  错误信息: %s\n", result.Error)
		fmt.Printf("  错误类型: 请求超时\n")
	}
}

// demonstrateStatusCodeErrors 演示状态码错误处理
func demonstrateStatusCodeErrors() {
	statusCodes := []int{400, 401, 404, 500}

	for _, code := range statusCodes {
		fmt.Printf("测试HTTP %d错误:\n", code)

		url := fmt.Sprintf("https://httpbin.org/status/%d", code)
		result := apitest.QuickTest("GET", url,
			apitest.WithExpectedStatus(200), // 期望200，但实际返回错误码
			apitest.WithTimeout(10*time.Second),
		)

		fmt.Printf("  测试结果: %s\n", getStatusText(result.Success))
		fmt.Printf("  实际状态码: %d\n", result.Response.StatusCode)

		if !result.Success {
			fmt.Printf("  错误信息: %s\n", result.Error)
		}

		fmt.Println()
	}
}

// demonstrateAssertionErrors 演示断言失败处理
func demonstrateAssertionErrors() {
	fmt.Println("测试断言失败场景:")

	// 测试不存在的字段断言
	result := apitest.QuickTest("GET", "https://httpbin.org/json",
		apitest.WithAssertions(
			apitest.CreateAssertion("exists", "body.nonexistent_field", nil, "不存在的字段"),
			apitest.CreateAssertion("equals", "body.slideshow.title", "Wrong Title", "错误的标题值"),
		),
	)

	fmt.Printf("  测试结果: %s\n", getStatusText(result.Success))
	fmt.Printf("  断言总数: %d\n", len(result.Assertions))

	for i, assertion := range result.Assertions {
		status := "✓"
		if !assertion.Success {
			status = "✗"
		}

		fmt.Printf("    断言%d %s: %s\n", i+1, status, assertion.Message)

		if !assertion.Success {
			fmt.Printf("      失败原因: 断言失败\n")
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
