package main

import (
	"fmt"
	"log"
	"time"

	"github.com/kweaver-ai/decision-agent/agent-factory/tool/apitesttool/apitest"
)

func main() {
	fmt.Println("=== API性能测试示例 ===\n")

	// 示例1: 并发性能测试
	fmt.Println("1. 并发性能测试")
	performanceConcurrentTest()

	fmt.Println("\n2. 负载测试")
	performanceLoadTest()

	fmt.Println("\n3. 压力测试")
	performanceStressTest()

	fmt.Println("\n4. 响应时间分析")
	performanceResponseTimeAnalysis()
}

// performanceConcurrentTest 并发性能测试
func performanceConcurrentTest() {
	tester := apitest.New()

	// 创建性能测试配置
	configData := `{
		"name": "并发性能测试",
		"description": "测试API在并发请求下的性能表现",
		"tests": [
			{
				"name": "GET性能测试",
				"request": {
					"method": "GET",
					"url": "https://httpbin.org/get",
					"params": {
						"test_id": "${random_number:1-10000}",
						"timestamp": "${timestamp}"
					}
				},
				"expected": {
					"status_code": 200
				},
				"timeout": "10s"
			},
			{
				"name": "POST性能测试",
				"request": {
					"method": "POST",
					"url": "https://httpbin.org/post",
					"headers": {
						"Content-Type": "application/json"
					},
					"body": {
						"user_id": "${random_number:1000-9999}",
						"data": "${random_string:100}",
						"timestamp": "${timestamp_ms}"
					}
				},
				"expected": {
					"status_code": 200
				},
				"timeout": "10s"
			}
		]
	}`

	config, err := tester.LoadConfigFromString(configData, "json")
	if err != nil {
		log.Printf("加载配置失败: %v", err)
		return
	}

	// 复制测试用例以增加负载
	originalTests := config.Tests
	for i := 0; i < 10; i++ { // 每个测试重复10次
		config.Tests = append(config.Tests, originalTests...)
	}

	fmt.Printf("总测试数量: %d\n", len(config.Tests))

	// 串行执行测试
	fmt.Println("串行执行测试...")

	startTime := time.Now()

	serialReport, err := tester.RunTests(config)
	if err != nil {
		log.Printf("串行测试失败: %v", err)
		return
	}

	serialDuration := time.Since(startTime)

	// 并发执行测试
	fmt.Println("并发执行测试...")

	startTime = time.Now()

	parallelReport, err := tester.RunTests(config, apitest.WithParallel(10))
	if err != nil {
		log.Printf("并发测试失败: %v", err)
		return
	}

	parallelDuration := time.Since(startTime)

	// 性能对比
	fmt.Printf("\n性能对比结果:\n")
	fmt.Printf("串行执行时间: %v\n", serialDuration.Round(time.Millisecond))
	fmt.Printf("并发执行时间: %v\n", parallelDuration.Round(time.Millisecond))
	fmt.Printf("性能提升: %.2fx\n", float64(serialDuration)/float64(parallelDuration))
	fmt.Printf("串行成功率: %.1f%%\n", serialReport.SuccessRate)
	fmt.Printf("并发成功率: %.1f%%\n", parallelReport.SuccessRate)
}

// performanceLoadTest 负载测试
func performanceLoadTest() {
	fmt.Println("执行负载测试 - 模拟正常用户负载")

	// 创建多个并发用户的测试场景
	userCounts := []int{1, 5, 10, 20}

	for _, userCount := range userCounts {
		fmt.Printf("\n测试 %d 个并发用户:\n", userCount)

		// 创建测试配置
		tests := make([]apitest.APITest, userCount)
		for i := 0; i < userCount; i++ {
			tests[i] = apitest.APITest{
				Name: fmt.Sprintf("用户%d请求", i+1),
				Request: apitest.RequestConfig{
					Method: "GET",
					URL:    "https://httpbin.org/delay/1",
					Headers: map[string]string{
						"User-Agent": fmt.Sprintf("LoadTest-User-%d", i+1),
					},
					Params: map[string]string{
						"user_id": fmt.Sprintf("%d", i+1),
						"test_id": "${random_number}",
					},
				},
				Expected: apitest.ExpectedResponse{
					StatusCode: 200,
				},
				Timeout: apitest.Duration(15 * time.Second),
			}
		}

		tester := apitest.New()
		startTime := time.Now()

		// 创建临时配置并执行测试
		config := &apitest.TestConfig{
			Name:  "负载测试",
			Tests: tests,
		}

		report, err := tester.RunTests(config, apitest.WithParallel(userCount))
		if err != nil {
			fmt.Printf("  测试失败: %v\n", err)
			continue
		}

		duration := time.Since(startTime)
		results := report.Results

		// 计算统计信息
		successCount := 0
		totalResponseTime := time.Duration(0)
		minResponseTime := time.Duration(0)
		maxResponseTime := time.Duration(0)

		for i, result := range results {
			if result.Success {
				successCount++
			}

			totalResponseTime += result.Duration

			if i == 0 || result.Duration < minResponseTime {
				minResponseTime = result.Duration
			}

			if result.Duration > maxResponseTime {
				maxResponseTime = result.Duration
			}
		}

		avgResponseTime := totalResponseTime / time.Duration(len(results))
		successRate := float64(successCount) / float64(len(results)) * 100

		fmt.Printf("  总耗时: %v\n", duration.Round(time.Millisecond))
		fmt.Printf("  成功率: %.1f%% (%d/%d)\n", successRate, successCount, len(results))
		fmt.Printf("  平均响应时间: %v\n", avgResponseTime.Round(time.Millisecond))
		fmt.Printf("  最小响应时间: %v\n", minResponseTime.Round(time.Millisecond))
		fmt.Printf("  最大响应时间: %v\n", maxResponseTime.Round(time.Millisecond))
		fmt.Printf("  吞吐量: %.2f 请求/秒\n", float64(len(results))/duration.Seconds())
	}
}

// performanceStressTest 压力测试
func performanceStressTest() {
	fmt.Println("执行压力测试 - 测试系统极限")

	tester := apitest.New()

	// 创建大量测试用例
	var tests []apitest.APITest

	testCount := 50 // 50个并发请求

	for i := 0; i < testCount; i++ {
		test := apitest.APITest{
			Name: fmt.Sprintf("压力测试-%d", i+1),
			Request: apitest.RequestConfig{
				Method: "POST",
				URL:    "https://httpbin.org/post",
				Headers: map[string]string{
					"Content-Type": "application/json",
					"X-Test-ID":    fmt.Sprintf("stress-test-%d", i+1),
				},
				Body: map[string]interface{}{
					"test_id":   i + 1,
					"data":      "${random_string:500}", // 大量数据
					"timestamp": "${timestamp_ms}",
					"uuid":      "${uuid}",
				},
			},
			Expected: apitest.ExpectedResponse{
				StatusCode: 200,
			},
			Timeout: apitest.Duration(30 * time.Second),
		}
		tests = append(tests, test)
	}

	fmt.Printf("开始压力测试 - %d 个并发请求\n", testCount)

	startTime := time.Now()

	// 创建临时配置并执行高并发测试
	config := &apitest.TestConfig{
		Name:  "压力测试",
		Tests: tests,
	}

	report, err := tester.RunTests(config,
		apitest.WithParallel(20), // 20个并发
		apitest.WithVerbose(false),
	)
	if err != nil {
		fmt.Printf("压力测试失败: %v\n", err)
		return
	}

	duration := time.Since(startTime)
	results := report.Results

	// 分析结果
	successCount := 0
	errorCount := 0
	timeoutCount := 0

	var responseTimes []time.Duration

	for _, result := range results {
		if result.Success {
			successCount++
		} else {
			errorCount++

			if result.Duration > 25*time.Second {
				timeoutCount++
			}
		}

		responseTimes = append(responseTimes, result.Duration)
	}

	// 计算百分位数
	p95, p99 := calculatePercentiles(responseTimes)

	fmt.Printf("\n压力测试结果:\n")
	fmt.Printf("总请求数: %d\n", len(results))
	fmt.Printf("成功请求: %d\n", successCount)
	fmt.Printf("失败请求: %d\n", errorCount)
	fmt.Printf("超时请求: %d\n", timeoutCount)
	fmt.Printf("成功率: %.1f%%\n", float64(successCount)/float64(len(results))*100)
	fmt.Printf("总耗时: %v\n", duration.Round(time.Millisecond))
	fmt.Printf("吞吐量: %.2f 请求/秒\n", float64(len(results))/duration.Seconds())
	fmt.Printf("P95响应时间: %v\n", p95.Round(time.Millisecond))
	fmt.Printf("P99响应时间: %v\n", p99.Round(time.Millisecond))
}

// performanceResponseTimeAnalysis 响应时间分析
func performanceResponseTimeAnalysis() {
	fmt.Println("执行响应时间分析")

	// 测试不同的延迟场景
	delays := []int{0, 1, 2, 5}

	for _, delay := range delays {
		fmt.Printf("\n测试 %d 秒延迟:\n", delay)

		url := fmt.Sprintf("https://httpbin.org/delay/%d", delay)

		// 执行多次测试获取稳定数据
		var responseTimes []time.Duration

		testCount := 5

		for i := 0; i < testCount; i++ {
			result := apitest.QuickTest("GET", url,
				apitest.WithTimeout(time.Duration(delay+10)*time.Second),
				apitest.WithHeaders(map[string]string{
					"X-Test-Round": fmt.Sprintf("%d", i+1),
				}),
			)

			if result.Success {
				responseTimes = append(responseTimes, result.Duration)
			}
		}

		if len(responseTimes) > 0 {
			// 计算统计信息
			var total time.Duration

			min := responseTimes[0]
			max := responseTimes[0]

			for _, rt := range responseTimes {
				total += rt

				if rt < min {
					min = rt
				}

				if rt > max {
					max = rt
				}
			}

			avg := total / time.Duration(len(responseTimes))

			fmt.Printf("  成功测试: %d/%d\n", len(responseTimes), testCount)
			fmt.Printf("  平均响应时间: %v\n", avg.Round(time.Millisecond))
			fmt.Printf("  最小响应时间: %v\n", min.Round(time.Millisecond))
			fmt.Printf("  最大响应时间: %v\n", max.Round(time.Millisecond))
			fmt.Printf("  响应时间标准差: %v\n", calculateStdDev(responseTimes, avg).Round(time.Millisecond))
		} else {
			fmt.Printf("  所有测试都失败了\n")
		}
	}
}

// calculatePercentiles 计算百分位数
func calculatePercentiles(durations []time.Duration) (p95, p99 time.Duration) {
	if len(durations) == 0 {
		return 0, 0
	}

	// 简单排序
	for i := 0; i < len(durations)-1; i++ {
		for j := 0; j < len(durations)-i-1; j++ {
			if durations[j] > durations[j+1] {
				durations[j], durations[j+1] = durations[j+1], durations[j]
			}
		}
	}

	p95Index := int(float64(len(durations)) * 0.95)
	p99Index := int(float64(len(durations)) * 0.99)

	if p95Index >= len(durations) {
		p95Index = len(durations) - 1
	}

	if p99Index >= len(durations) {
		p99Index = len(durations) - 1
	}

	return durations[p95Index], durations[p99Index]
}

// calculateStdDev 计算标准差
func calculateStdDev(durations []time.Duration, avg time.Duration) time.Duration {
	if len(durations) <= 1 {
		return 0
	}

	var sum float64

	avgFloat := float64(avg)

	for _, d := range durations {
		diff := float64(d) - avgFloat
		sum += diff * diff
	}

	variance := sum / float64(len(durations)-1)
	stdDev := time.Duration(sqrt(variance))

	return stdDev
}

// sqrt 简单的平方根计算
func sqrt(x float64) float64 {
	if x == 0 {
		return 0
	}

	// 牛顿法求平方根
	z := x
	for i := 0; i < 10; i++ {
		z = (z + x/z) / 2
	}

	return z
}
