package main

import (
	"flag"
	"fmt"
	"os"
	"time"

	"github.com/kweaver-ai/decision-agent/agent-factory/tool/apitesttool/apitest"
)

func main() {
	// 命令行参数
	var (
		configFile   = flag.String("config", "", "测试配置文件路径 (JSON或YAML格式)")
		reportFormat = flag.String("format", "console", "报告格式 (console, json, html)")
		outputPath   = flag.String("output", "", "报告输出路径")
		parallel     = flag.Int("parallel", 1, "并发执行的测试数量")
		verbose      = flag.Bool("verbose", false, "详细输出模式")
		help         = flag.Bool("help", false, "显示帮助信息")
	)

	flag.Parse()

	if *help || *configFile == "" {
		printUsage()
		return
	}

	// 检查配置文件是否存在
	if _, err := os.Stat(*configFile); os.IsNotExist(err) {
		fmt.Printf("错误: 配置文件不存在: %s\n", *configFile)
		os.Exit(1)
	}

	// 创建API测试器
	tester := apitest.New()

	// 加载测试配置
	config, err := tester.LoadConfigFromFile(*configFile)
	if err != nil {
		fmt.Printf("错误: 加载配置文件失败: %v\n", err)
		os.Exit(1)
	}

	if *verbose {
		fmt.Printf("加载配置文件: %s\n", *configFile)
		fmt.Printf("测试名称: %s\n", config.Name)
		fmt.Printf("测试数量: %d\n", len(config.Tests))
		fmt.Printf("并发数: %d\n", *parallel)
		fmt.Printf("报告格式: %s\n", *reportFormat)
		fmt.Println()
	}

	// 执行测试
	fmt.Printf("开始执行API测试...\n")

	startTime := time.Now()

	// 设置执行选项
	var options []apitest.ExecuteOption
	if *parallel > 1 {
		options = append(options, apitest.WithParallel(*parallel))
	}

	if *verbose {
		options = append(options, apitest.WithVerbose(true))
	}

	report, err := tester.RunTestsWithConfigInfo(config, *configFile, *reportFormat, *parallel, *verbose, options...)
	if err != nil {
		fmt.Printf("错误: 执行测试失败: %v\n", err)
		os.Exit(1)
	}

	duration := time.Since(startTime)
	fmt.Printf("测试执行完成，耗时: %v\n", duration.Round(time.Millisecond))

	// 输出报告
	err = tester.GenerateReport(report, *reportFormat, *outputPath)
	if err != nil {
		fmt.Printf("错误: 生成报告失败: %v\n", err)
		os.Exit(1)
	}

	// 根据测试结果设置退出码
	if report.FailedTests > 0 {
		os.Exit(1)
	}
}

// printUsage 打印使用说明
func printUsage() {
	fmt.Println("API测试工具")
	fmt.Println()
	fmt.Println("用法:")
	fmt.Println("  go run . -config <配置文件> [选项]")
	fmt.Println()
	fmt.Println("选项:")
	fmt.Println("  -config string    测试配置文件路径 (JSON或YAML格式)")
	fmt.Println("  -format string    报告格式: console, json, html (默认: console)")
	fmt.Println("  -output string    报告输出路径 (可选)")
	fmt.Println("  -parallel int     并发执行的测试数量 (默认: 1)")
	fmt.Println("  -verbose          详细输出模式")
	fmt.Println("  -help             显示此帮助信息")
	fmt.Println()
	fmt.Println("示例:")
	fmt.Println("  go run . -config test.json")
	fmt.Println("  go run . -config test.yaml -format html -output report.html")
	fmt.Println("  go run . -config test.json -parallel 5 -verbose")
}
