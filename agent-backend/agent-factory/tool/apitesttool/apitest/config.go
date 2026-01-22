package apitest

import (
	"encoding/json"
	"time"
)

// Duration 自定义Duration类型，支持JSON解析
type Duration time.Duration

// UnmarshalJSON 实现JSON反序列化
func (d *Duration) UnmarshalJSON(data []byte) error {
	var s string
	if err := json.Unmarshal(data, &s); err != nil {
		return err
	}

	duration, err := time.ParseDuration(s)
	if err != nil {
		return err
	}

	*d = Duration(duration)

	return nil
}

// MarshalJSON 实现JSON序列化
func (d Duration) MarshalJSON() ([]byte, error) {
	return json.Marshal(time.Duration(d).String())
}

// String 返回字符串表示
func (d Duration) String() string {
	return time.Duration(d).String()
}

// UnmarshalYAML 实现YAML反序列化
func (d *Duration) UnmarshalYAML(unmarshal func(interface{}) error) error {
	var s string
	if err := unmarshal(&s); err != nil {
		return err
	}

	duration, err := time.ParseDuration(s)
	if err != nil {
		return err
	}

	*d = Duration(duration)

	return nil
}

// MarshalYAML 实现YAML序列化
func (d Duration) MarshalYAML() (interface{}, error) {
	return time.Duration(d).String(), nil
}

// TestConfig 测试配置结构
type TestConfig struct {
	Name           string            `json:"name" yaml:"name"`                       // 测试名称
	Description    string            `json:"description" yaml:"description"`         // 测试描述
	Tests          []APITest         `json:"tests" yaml:"tests"`                     // 测试用例列表
	Variables      map[string]string `json:"variables" yaml:"variables"`             // 全局变量
	VariableConfig VariableConfig    `json:"variable_config" yaml:"variable_config"` // 变量配置
}

// APITest API测试用例
type APITest struct {
	Name               string               `json:"name" yaml:"name"`                               // 测试用例名称
	Description        string               `json:"description" yaml:"description"`                 // 测试用例描述
	Request            RequestConfig        `json:"request" yaml:"request"`                         // 请求配置
	Expected           ExpectedResponse     `json:"expected" yaml:"expected"`                       // 期望响应
	Timeout            Duration             `json:"timeout" yaml:"timeout"`                         // 超时时间
	Retry              int                  `json:"retry" yaml:"retry"`                             // 重试次数
	Variables          map[string]string    `json:"variables" yaml:"variables"`                     // 变量定义
	VariableExtraction []VariableExtraction `json:"variable_extraction" yaml:"variable_extraction"` // 变量提取配置
}

// RequestConfig 请求配置
type RequestConfig struct {
	Method  string            `json:"method" yaml:"method"`   // 请求方法 GET/POST/PUT/DELETE等
	URL     string            `json:"url" yaml:"url"`         // 完整URL或者使用Host+Path
	Host    string            `json:"host" yaml:"host"`       // 主机地址
	Path    string            `json:"path" yaml:"path"`       // 请求路径
	Headers map[string]string `json:"headers" yaml:"headers"` // 请求头
	Params  map[string]string `json:"params" yaml:"params"`   // URL参数
	Body    interface{}       `json:"body" yaml:"body"`       // 请求体
}

// ExpectedResponse 期望响应
type ExpectedResponse struct {
	StatusCode int                    `json:"status_code" yaml:"status_code"` // 期望状态码
	Headers    map[string]string      `json:"headers" yaml:"headers"`         // 期望响应头
	Body       interface{}            `json:"body" yaml:"body"`               // 期望响应体
	Assertions []AssertionConfig      `json:"assertions" yaml:"assertions"`   // 断言配置
	JSONPath   map[string]interface{} `json:"json_path" yaml:"json_path"`     // JSONPath断言
}

// AssertionConfig 断言配置
type AssertionConfig struct {
	Type     string      `json:"type" yaml:"type"`         // 断言类型: equals, contains, regex, exists, not_exists
	Field    string      `json:"field" yaml:"field"`       // 断言字段路径
	Value    interface{} `json:"value" yaml:"value"`       // 期望值
	Message  string      `json:"message" yaml:"message"`   // 断言失败消息
	Optional bool        `json:"optional" yaml:"optional"` // 是否可选断言
}

// TestResult 测试结果
type TestResult struct {
	TestName   string            `json:"test_name"`
	Success    bool              `json:"success"`
	Duration   time.Duration     `json:"duration"`
	Request    RequestInfo       `json:"request"`
	Response   ResponseInfo      `json:"response"`
	Assertions []AssertionResult `json:"assertions"`
	Error      string            `json:"error,omitempty"`
	Variables  map[string]string `json:"variables,omitempty"`
	RetryCount int               `json:"retry_count"`
}

// RequestInfo 请求信息
type RequestInfo struct {
	Method  string            `json:"method"`
	URL     string            `json:"url"`
	Headers map[string]string `json:"headers"`
	Body    string            `json:"body,omitempty"`
}

// ResponseInfo 响应信息
type ResponseInfo struct {
	StatusCode int               `json:"status_code"`
	Headers    map[string]string `json:"headers"`
	Body       string            `json:"body"`
	Size       int64             `json:"size"`
}

// AssertionResult 断言结果
type AssertionResult struct {
	Type     string      `json:"type"`
	Field    string      `json:"field"`
	Expected interface{} `json:"expected"`
	Actual   interface{} `json:"actual"`
	Success  bool        `json:"success"`
	Message  string      `json:"message"`
	Optional bool        `json:"optional"`
}

// ConfigInfo 配置信息
type ConfigInfo struct {
	ConfigFile   string            `json:"config_file,omitempty"`
	ConfigFormat string            `json:"config_format,omitempty"`
	Parallel     int               `json:"parallel,omitempty"`
	ReportFormat string            `json:"report_format,omitempty"`
	Verbose      bool              `json:"verbose,omitempty"`
	Variables    map[string]string `json:"variables,omitempty"`
}

// TestReport 测试报告
type TestReport struct {
	Name        string        `json:"name"`
	Description string        `json:"description"`
	StartTime   time.Time     `json:"start_time"`
	EndTime     time.Time     `json:"end_time"`
	Duration    time.Duration `json:"duration"`
	TotalTests  int           `json:"total_tests"`
	PassedTests int           `json:"passed_tests"`
	FailedTests int           `json:"failed_tests"`
	SuccessRate float64       `json:"success_rate"`
	Results     []TestResult  `json:"results"`
	ConfigInfo  *ConfigInfo   `json:"config_info,omitempty"`
}
