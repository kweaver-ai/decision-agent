package apitest

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"gopkg.in/yaml.v3"
)

// APITester API测试器主接口
type APITester struct {
	executor        *Executor
	reporter        *Reporter
	variableManager *VariableManager
}

// New 创建新的API测试器
func New() *APITester {
	vm := NewVariableManager()

	return &APITester{
		executor:        NewExecutorWithVariableManager(vm),
		reporter:        NewReporter(),
		variableManager: vm,
	}
}

// NewWithExecutor 使用自定义执行器创建API测试器
func NewWithExecutor(executor *Executor) *APITester {
	return &APITester{
		executor:        executor,
		reporter:        NewReporter(),
		variableManager: executor.variableManager,
	}
}

// NewWithVariableConfig 使用变量配置创建API测试器
func NewWithVariableConfig(config VariableConfig) *APITester {
	vm := NewVariableManagerWithConfig(config)

	return &APITester{
		executor:        NewExecutorWithVariableManager(vm),
		reporter:        NewReporter(),
		variableManager: vm,
	}
}

// LoadConfigFromFile 从文件加载测试配置
func (t *APITester) LoadConfigFromFile(configPath string) (*TestConfig, error) {
	data, err := os.ReadFile(configPath)
	if err != nil {
		return nil, fmt.Errorf("读取配置文件失败: %v", err)
	}

	var config TestConfig

	ext := filepath.Ext(configPath)

	switch ext {
	case ".json":
		err = json.Unmarshal(data, &config)
	case ".yaml", ".yml":
		err = yaml.Unmarshal(data, &config)
	default:
		// 尝试JSON格式
		err = json.Unmarshal(data, &config)
		if err != nil {
			// 如果JSON失败，尝试YAML格式
			err = yaml.Unmarshal(data, &config)
		}
	}

	if err != nil {
		return nil, fmt.Errorf("解析配置文件失败: %v", err)
	}

	// 验证和设置默认值
	t.validateAndSetDefaults(&config)

	return &config, nil
}

// LoadConfigFromString 从字符串加载测试配置
func (t *APITester) LoadConfigFromString(configData string, format string) (*TestConfig, error) {
	var config TestConfig

	var err error

	switch format {
	case "json":
		err = json.Unmarshal([]byte(configData), &config)
	case "yaml", "yml":
		err = yaml.Unmarshal([]byte(configData), &config)
	default:
		return nil, fmt.Errorf("不支持的配置格式: %s", format)
	}

	if err != nil {
		return nil, fmt.Errorf("解析配置失败: %v", err)
	}

	// 验证和设置默认值
	t.validateAndSetDefaults(&config)

	return &config, nil
}

// RunTests 执行测试套件
func (t *APITester) RunTests(config *TestConfig, options ...ExecuteOption) (*TestReport, error) {
	if config == nil {
		return nil, fmt.Errorf("配置不能为空")
	}

	if len(config.Tests) == 0 {
		return nil, fmt.Errorf("没有定义测试用例")
	}

	// 设置全局变量
	if config.Variables != nil {
		t.variableManager.SetVariables(config.Variables)
	}

	// 更新变量配置
	if config.VariableConfig.RandomNumberMin != 0 || config.VariableConfig.RandomNumberMax != 0 {
		t.variableManager.config = config.VariableConfig
	}

	// 执行测试
	results := t.executor.ExecuteTests(config.Tests, options...)

	// 创建配置信息
	configInfo := &ConfigInfo{
		Variables: config.Variables,
	}

	// 生成报告
	report := CreateTestReportWithConfig(*config, results, configInfo)

	return &report, nil
}

// RunTestsWithConfigInfo 执行测试并包含配置信息
func (t *APITester) RunTestsWithConfigInfo(config *TestConfig, configFile, reportFormat string, parallel int, verbose bool, options ...ExecuteOption) (*TestReport, error) {
	// 验证配置
	if config == nil {
		return nil, fmt.Errorf("配置不能为空")
	}

	// 设置默认值
	t.validateAndSetDefaults(config)

	// 设置全局变量
	if config.Variables != nil {
		t.variableManager.SetVariables(config.Variables)
	}

	// 更新变量配置
	if config.VariableConfig.RandomNumberMin != 0 || config.VariableConfig.RandomNumberMax != 0 {
		t.variableManager.config = config.VariableConfig
	}

	// 执行测试
	results := t.executor.ExecuteTests(config.Tests, options...)

	// 确定配置格式
	configFormat := "JSON"
	if strings.HasSuffix(strings.ToLower(configFile), ".yaml") || strings.HasSuffix(strings.ToLower(configFile), ".yml") {
		configFormat = "YAML"
	}

	// 创建配置信息
	configInfo := &ConfigInfo{
		ConfigFile:   configFile,
		ConfigFormat: configFormat,
		Parallel:     parallel,
		ReportFormat: reportFormat,
		Verbose:      verbose,
		Variables:    config.Variables,
	}

	// 生成报告
	report := CreateTestReportWithConfig(*config, results, configInfo)

	return &report, nil
}

// RunSingleTest 执行单个测试用例
func (t *APITester) RunSingleTest(test APITest) TestResult {
	// 设置默认值
	if test.Name == "" {
		test.Name = "单个测试"
	}

	if test.Request.Method == "" {
		test.Request.Method = "GET"
	}

	if test.Timeout == 0 {
		test.Timeout = Duration(30 * time.Second)
	}

	if test.Variables == nil {
		test.Variables = make(map[string]string)
	}

	return t.executor.ExecuteTest(test)
}

// GenerateReport 生成测试报告
func (t *APITester) GenerateReport(report *TestReport, format string, outputPath string) error {
	return t.reporter.GenerateReport(*report, format, outputPath)
}

// PrintReport 打印控制台报告
func (t *APITester) PrintReport(report *TestReport) {
	t.reporter.PrintConsoleReport(*report)
}

// SetVariable 设置变量
func (t *APITester) SetVariable(name, value string) {
	t.variableManager.SetVariable(name, value)
}

// GetVariable 获取变量
func (t *APITester) GetVariable(name string) (string, bool) {
	return t.variableManager.GetVariable(name)
}

// SetVariables 批量设置变量
func (t *APITester) SetVariables(variables map[string]string) {
	t.variableManager.SetVariables(variables)
}

// GetAllVariables 获取所有变量
func (t *APITester) GetAllVariables() map[string]string {
	return t.variableManager.GetAllVariables()
}

// ClearVariables 清空所有变量
func (t *APITester) ClearVariables() {
	t.variableManager.ClearVariables()
}

// validateAndSetDefaults 验证配置并设置默认值
func (t *APITester) validateAndSetDefaults(config *TestConfig) {
	if config.Name == "" {
		config.Name = "API测试"
	}

	// 为每个测试设置默认值
	for i := range config.Tests {
		test := &config.Tests[i]
		if test.Name == "" {
			test.Name = fmt.Sprintf("测试用例 %d", i+1)
		}

		if test.Request.Method == "" {
			test.Request.Method = "GET"
		}

		if test.Timeout == 0 {
			test.Timeout = Duration(30 * time.Second)
		}

		if test.Retry < 0 {
			test.Retry = 0
		}

		if test.Variables == nil {
			test.Variables = make(map[string]string)
		}
	}
}

// QuickTest 快速测试单个API端点
func QuickTest(method, url string, options ...QuickTestOption) TestResult {
	test := APITest{
		Name: fmt.Sprintf("快速测试 %s %s", method, url),
		Request: RequestConfig{
			Method: method,
			URL:    url,
		},
		Timeout:   Duration(30 * time.Second),
		Variables: make(map[string]string),
	}

	// 应用选项
	for _, option := range options {
		option(&test)
	}

	executor := NewExecutor()

	return executor.ExecuteTest(test)
}

// QuickTestOption 快速测试选项
type QuickTestOption func(*APITest)

// WithHeaders 设置请求头
func WithHeaders(headers map[string]string) QuickTestOption {
	return func(test *APITest) {
		if test.Request.Headers == nil {
			test.Request.Headers = make(map[string]string)
		}

		for k, v := range headers {
			test.Request.Headers[k] = v
		}
	}
}

// WithBody 设置请求体
func WithBody(body interface{}) QuickTestOption {
	return func(test *APITest) {
		test.Request.Body = body
	}
}

// WithParams 设置URL参数
func WithParams(params map[string]string) QuickTestOption {
	return func(test *APITest) {
		if test.Request.Params == nil {
			test.Request.Params = make(map[string]string)
		}

		for k, v := range params {
			test.Request.Params[k] = v
		}
	}
}

// WithTimeout 设置超时时间
func WithTimeout(timeout time.Duration) QuickTestOption {
	return func(test *APITest) {
		test.Timeout = Duration(timeout)
	}
}

// WithExpectedStatus 设置期望状态码
func WithExpectedStatus(statusCode int) QuickTestOption {
	return func(test *APITest) {
		test.Expected.StatusCode = statusCode
	}
}

// WithAssertions 设置断言
func WithAssertions(assertions ...AssertionConfig) QuickTestOption {
	return func(test *APITest) {
		test.Expected.Assertions = append(test.Expected.Assertions, assertions...)
	}
}

// WithVariables 设置变量
func WithVariables(variables map[string]string) QuickTestOption {
	return func(test *APITest) {
		if test.Variables == nil {
			test.Variables = make(map[string]string)
		}

		for k, v := range variables {
			test.Variables[k] = v
		}
	}
}

// WithVariableExtraction 设置变量提取
func WithVariableExtraction(extractions ...VariableExtraction) QuickTestOption {
	return func(test *APITest) {
		test.VariableExtraction = append(test.VariableExtraction, extractions...)
	}
}

// CreateAssertion 创建断言的辅助函数
func CreateAssertion(assertionType, field string, value interface{}, message string) AssertionConfig {
	return AssertionConfig{
		Type:    assertionType,
		Field:   field,
		Value:   value,
		Message: message,
	}
}

// CreateOptionalAssertion 创建可选断言的辅助函数
func CreateOptionalAssertion(assertionType, field string, value interface{}, message string) AssertionConfig {
	return AssertionConfig{
		Type:     assertionType,
		Field:    field,
		Value:    value,
		Message:  message,
		Optional: true,
	}
}
