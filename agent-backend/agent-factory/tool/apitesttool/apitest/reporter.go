package apitest

import (
	_ "embed"
	"encoding/json"
	"fmt"
	"html/template"
	"os"
	"strings"
	"time"
)

//go:embed templates/report.html
var htmlTemplate string

// Reporter 报告生成器
type Reporter struct{}

// NewReporter 创建新的报告生成器
func NewReporter() *Reporter {
	return &Reporter{}
}

// GenerateReport 生成测试报告
func (r *Reporter) GenerateReport(report TestReport, format string, outputPath string) error {
	switch strings.ToLower(format) {
	case "json":
		return r.generateJSONReport(report, outputPath)
	case "html":
		return r.generateHTMLReport(report, outputPath)
	case "console":
		r.PrintConsoleReport(report)
		return nil
	default:
		return fmt.Errorf("不支持的报告格式: %s", format)
	}
}

// generateJSONReport 生成JSON格式报告
func (r *Reporter) generateJSONReport(report TestReport, outputPath string) error {
	jsonData, err := json.MarshalIndent(report, "", "  ")
	if err != nil {
		return fmt.Errorf("序列化JSON报告失败: %v", err)
	}

	if outputPath == "" {
		outputPath = fmt.Sprintf("test_report_%s.json", time.Now().Format("20060102_150405"))
	}

	err = os.WriteFile(outputPath, jsonData, 0o644)
	if err != nil {
		return fmt.Errorf("写入JSON报告文件失败: %v", err)
	}

	fmt.Printf("JSON报告已生成: %s\n", outputPath)

	return nil
}

// generateHTMLReport 生成HTML格式报告
func (r *Reporter) generateHTMLReport(report TestReport, outputPath string) error {
	if outputPath == "" {
		outputPath = fmt.Sprintf("test_report_%s.html", time.Now().Format("20060102_150405"))
	}

	tmpl, err := template.New("report").Funcs(template.FuncMap{
		"time": func() time.Time { return time.Now() },
		"add":  func(a, b int) int { return a + b },
		"formatDuration": func(d time.Duration) string {
			seconds := d.Seconds()
			if seconds < 1 {
				return fmt.Sprintf("%.2fms", d.Seconds()*1000)
			} else if seconds < 60 {
				return fmt.Sprintf("%.2fs", seconds)
			} else if seconds < 3600 {
				minutes := int(seconds / 60)
				remainingSeconds := seconds - float64(minutes*60)
				return fmt.Sprintf("%dm%.2fs", minutes, remainingSeconds)
			} else {
				hours := int(seconds / 3600)
				remainingMinutes := int((seconds - float64(hours*3600)) / 60)
				remainingSeconds := seconds - float64(hours*3600) - float64(remainingMinutes*60)
				return fmt.Sprintf("%dh%dm%.2fs", hours, remainingMinutes, remainingSeconds)
			}
		},
	}).Parse(htmlTemplate)
	if err != nil {
		return fmt.Errorf("解析HTML模板失败: %v", err)
	}

	file, err := os.Create(outputPath)
	if err != nil {
		return fmt.Errorf("创建HTML报告文件失败: %v", err)
	}
	defer file.Close()

	err = tmpl.Execute(file, report)
	if err != nil {
		return fmt.Errorf("生成HTML报告失败: %v", err)
	}

	fmt.Printf("HTML报告已生成: %s\n", outputPath)

	return nil
}

// PrintConsoleReport 打印控制台报告
func (r *Reporter) PrintConsoleReport(report TestReport) {
	fmt.Println(strings.Repeat("=", 80))
	fmt.Printf("API测试报告: %s\n", report.Name)

	if report.Description != "" {
		fmt.Printf("描述: %s\n", report.Description)
	}

	fmt.Printf("测试时间: %s - %s\n",
		report.StartTime.Format("2006-01-02 15:04:05"),
		report.EndTime.Format("2006-01-02 15:04:05"))
	fmt.Printf("总耗时: %v\n", report.Duration.Round(time.Millisecond))
	fmt.Println(strings.Repeat("=", 80))

	// 汇总信息
	fmt.Printf("总测试数: %d\n", report.TotalTests)
	fmt.Printf("通过测试: %d\n", report.PassedTests)
	fmt.Printf("失败测试: %d\n", report.FailedTests)
	fmt.Printf("成功率: %.1f%%\n", report.SuccessRate)
	fmt.Println()

	// 详细结果
	for i, result := range report.Results {
		fmt.Printf("[%d] %s", i+1, result.TestName)

		if result.Success {
			fmt.Printf(" ✓ 通过")
		} else {
			fmt.Printf(" ✗ 失败")
		}

		fmt.Printf(" (%v)", result.Duration.Round(time.Millisecond))

		if result.RetryCount > 0 {
			fmt.Printf(" (重试 %d 次)", result.RetryCount)
		}

		fmt.Println()

		if result.Error != "" {
			fmt.Printf("    错误: %s\n", result.Error)
		}

		// 请求信息
		fmt.Printf("    请求: %s %s\n", result.Request.Method, result.Request.URL)

		// 响应信息
		fmt.Printf("    响应: %d (%d bytes)\n", result.Response.StatusCode, result.Response.Size)

		// 断言结果
		if len(result.Assertions) > 0 {
			fmt.Println("    断言:")

			for _, assertion := range result.Assertions {
				status := "✗"
				if assertion.Success {
					status = "✓"
				}

				optional := ""
				if assertion.Optional {
					optional = " (可选)"
				}

				fmt.Printf("      %s %s (%s): %s%s\n",
					status, assertion.Type, assertion.Field, assertion.Message, optional)
			}
		}

		fmt.Println()
	}

	fmt.Println(strings.Repeat("=", 80))
}

// CreateTestReport 创建测试报告
func CreateTestReport(config TestConfig, results []TestResult) TestReport {
	return CreateTestReportWithConfig(config, results, nil)
}

// CreateTestReportWithConfig 创建带配置信息的测试报告
func CreateTestReportWithConfig(config TestConfig, results []TestResult, configInfo *ConfigInfo) TestReport {
	startTime := time.Now()
	endTime := time.Now()

	if len(results) > 0 {
		// 找到最早的开始时间和最晚的结束时间
		startTime = time.Now()
		endTime = time.Time{}

		for _, result := range results {
			// 由于我们没有记录每个测试的开始时间，这里使用当前时间减去持续时间作为估算
			testStart := time.Now().Add(-result.Duration)
			testEnd := time.Now()

			if testStart.Before(startTime) {
				startTime = testStart
			}

			if testEnd.After(endTime) {
				endTime = testEnd
			}
		}
	}

	totalTests := len(results)
	passedTests := 0
	failedTests := 0

	for _, result := range results {
		if result.Success {
			passedTests++
		} else {
			failedTests++
		}
	}

	successRate := 0.0
	if totalTests > 0 {
		successRate = float64(passedTests) / float64(totalTests) * 100
	}

	return TestReport{
		Name:        config.Name,
		Description: config.Description,
		StartTime:   startTime,
		EndTime:     endTime,
		Duration:    endTime.Sub(startTime),
		TotalTests:  totalTests,
		PassedTests: passedTests,
		FailedTests: failedTests,
		SuccessRate: successRate,
		Results:     results,
		ConfigInfo:  configInfo,
	}
}
