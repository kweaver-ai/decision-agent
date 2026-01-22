package apitest

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/tidwall/gjson"
)

// Executor API测试执行器
type Executor struct {
	client          *http.Client
	variableManager *VariableManager
}

// NewExecutor 创建新的API测试执行器
func NewExecutor() *Executor {
	return &Executor{
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
		variableManager: NewVariableManager(),
	}
}

// NewExecutorWithClient 使用自定义HTTP客户端创建执行器
func NewExecutorWithClient(client *http.Client) *Executor {
	return &Executor{
		client:          client,
		variableManager: NewVariableManager(),
	}
}

// NewExecutorWithVariableManager 使用自定义变量管理器创建执行器
func NewExecutorWithVariableManager(vm *VariableManager) *Executor {
	return &Executor{
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
		variableManager: vm,
	}
}

// ExecuteTest 执行单个测试用例
func (e *Executor) ExecuteTest(test APITest) TestResult {
	startTime := time.Now()
	result := TestResult{
		TestName:   test.Name,
		Success:    false,
		Variables:  make(map[string]string),
		RetryCount: 0,
	}

	// 设置重试次数
	maxRetries := 1
	if test.Retry > 0 {
		maxRetries = test.Retry + 1
	}

	// 执行测试，支持重试
	for attempt := 0; attempt < maxRetries; attempt++ {
		result.RetryCount = attempt

		// 执行HTTP请求
		req, resp, err := e.executeHTTPRequest(test.Request)
		if err != nil {
			result.Error = err.Error()

			if attempt < maxRetries-1 {
				time.Sleep(time.Second * time.Duration(attempt+1))
				continue
			}

			return result
		}

		// 记录请求和响应信息
		result.Request = req
		result.Response = resp

		// 执行断言
		assertions := e.executeAssertions(test.Expected, resp)
		result.Assertions = assertions

		// 检查是否所有必需断言都通过
		allPassed := true

		for _, assertion := range assertions {
			if !assertion.Success && !assertion.Optional {
				allPassed = false
				break
			}
		}

		if allPassed {
			result.Success = true
			// 只有在测试成功时才提取变量，避免重试时重复提取
			if len(test.VariableExtraction) > 0 {
				err := e.variableManager.ExtractVariables(test.VariableExtraction, resp)
				if err != nil {
					// 变量提取失败不影响测试结果，只记录警告
					fmt.Printf("警告: 变量提取失败: %v\n", err)
				}
			}

			break
		} else if attempt < maxRetries-1 {
			time.Sleep(time.Second * time.Duration(attempt+1))
			continue
		}
	}

	// 记录当前所有变量
	result.Variables = e.variableManager.GetAllVariables()
	result.Duration = time.Since(startTime)

	return result
}

// ExecuteTests 执行多个测试用例
func (e *Executor) ExecuteTests(tests []APITest, options ...ExecuteOption) []TestResult {
	opts := &ExecuteOptions{
		Parallel: 1,
		Verbose:  false,
	}

	for _, option := range options {
		option(opts)
	}

	if opts.Parallel <= 1 {
		return e.executeTestsSerial(tests, opts.Verbose)
	} else {
		return e.executeTestsParallel(tests, opts.Parallel, opts.Verbose)
	}
}

// ExecuteOptions 执行选项
type ExecuteOptions struct {
	Parallel int
	Verbose  bool
}

// ExecuteOption 执行选项函数
type ExecuteOption func(*ExecuteOptions)

// WithParallel 设置并发数
func WithParallel(parallel int) ExecuteOption {
	return func(opts *ExecuteOptions) {
		opts.Parallel = parallel
	}
}

// WithVerbose 设置详细输出
func WithVerbose(verbose bool) ExecuteOption {
	return func(opts *ExecuteOptions) {
		opts.Verbose = verbose
	}
}

// executeTestsSerial 串行执行测试
func (e *Executor) executeTestsSerial(tests []APITest, verbose bool) []TestResult {
	results := make([]TestResult, 0, len(tests))

	for i, test := range tests {
		if verbose {
			fmt.Printf("[%d/%d] 执行测试: %s\n", i+1, len(tests), test.Name)
		}

		result := e.ExecuteTest(test)
		results = append(results, result)

		if verbose {
			status := "通过"
			if !result.Success {
				status = "失败"
			}

			fmt.Printf("  结果: %s (%v)\n", status, result.Duration.Round(time.Millisecond))
		}
	}

	return results
}

// executeTestsParallel 并行执行测试
func (e *Executor) executeTestsParallel(tests []APITest, parallel int, verbose bool) []TestResult {
	results := make([]TestResult, len(tests))

	// 创建工作通道
	testChan := make(chan int, len(tests))
	resultChan := make(chan struct {
		index  int
		result TestResult
	}, len(tests))

	// 启动工作协程
	for i := 0; i < parallel; i++ {
		go func() {
			for testIndex := range testChan {
				test := tests[testIndex]
				if verbose {
					fmt.Printf("执行测试: %s\n", test.Name)
				}

				result := e.ExecuteTest(test)

				if verbose {
					status := "通过"
					if !result.Success {
						status = "失败"
					}

					fmt.Printf("  结果: %s - %s (%v)\n", test.Name, status, result.Duration.Round(time.Millisecond))
				}

				resultChan <- struct {
					index  int
					result TestResult
				}{testIndex, result}
			}
		}()
	}

	// 发送测试任务
	for i := range tests {
		testChan <- i
	}

	close(testChan)

	// 收集结果
	for i := 0; i < len(tests); i++ {
		result := <-resultChan
		results[result.index] = result.result
	}

	return results
}

// executeHTTPRequest 执行HTTP请求
func (e *Executor) executeHTTPRequest(reqConfig RequestConfig) (RequestInfo, ResponseInfo, error) {
	// 构建URL（已在buildURL中完成变量替换）
	requestURL := e.buildURL(reqConfig)

	// 准备请求体
	var bodyReader io.Reader

	var bodyStr string

	if reqConfig.Body != nil {
		bodyBytes, err := json.Marshal(reqConfig.Body)
		if err != nil {
			return RequestInfo{}, ResponseInfo{}, fmt.Errorf("序列化请求体失败: %v", err)
		}

		bodyStr = e.variableManager.ReplaceVariables(string(bodyBytes))
		bodyReader = bytes.NewReader([]byte(bodyStr))
	}

	// 创建HTTP请求
	req, err := http.NewRequest(strings.ToUpper(reqConfig.Method), requestURL, bodyReader)
	if err != nil {
		return RequestInfo{}, ResponseInfo{}, fmt.Errorf("创建HTTP请求失败: %v", err)
	}

	// 设置请求头
	for key, value := range reqConfig.Headers {
		req.Header.Set(key, e.variableManager.ReplaceVariables(value))
	}

	// 如果没有设置Content-Type且有请求体，默认设置为application/json
	if reqConfig.Body != nil && req.Header.Get("Content-Type") == "" {
		req.Header.Set("Content-Type", "application/json")
	}

	// 发送请求
	resp, err := e.client.Do(req)
	if err != nil {
		return RequestInfo{}, ResponseInfo{}, fmt.Errorf("发送HTTP请求失败: %v", err)
	}
	defer resp.Body.Close()

	// 读取响应体
	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return RequestInfo{}, ResponseInfo{}, fmt.Errorf("读取响应体失败: %v", err)
	}

	// 构建请求信息
	requestInfo := RequestInfo{
		Method:  req.Method,
		URL:     req.URL.String(),
		Headers: make(map[string]string),
		Body:    bodyStr,
	}

	for key, values := range req.Header {
		if len(values) > 0 {
			requestInfo.Headers[key] = values[0]
		}
	}

	// 构建响应信息
	responseInfo := ResponseInfo{
		StatusCode: resp.StatusCode,
		Headers:    make(map[string]string),
		Body:       string(respBody),
		Size:       int64(len(respBody)),
	}

	for key, values := range resp.Header {
		if len(values) > 0 {
			responseInfo.Headers[key] = values[0]
		}
	}

	return requestInfo, responseInfo, nil
}

// buildURL 构建完整URL
func (e *Executor) buildURL(reqConfig RequestConfig) string {
	var requestURL string

	if reqConfig.URL != "" {
		requestURL = reqConfig.URL
	} else {
		// 使用Host和Path构建URL
		host := reqConfig.Host
		if host == "" {
			host = "localhost"
		}

		if !strings.HasPrefix(host, "http://") && !strings.HasPrefix(host, "https://") {
			host = "http://" + host
		}

		path := reqConfig.Path
		if path == "" {
			path = "/"
		}

		if !strings.HasPrefix(path, "/") {
			path = "/" + path
		}

		requestURL = host + path
	}

	// 先替换URL中的模板变量（如{{base_url}}）
	requestURL = e.variableManager.ReplaceVariables(requestURL)

	// 智能处理URL中的特殊字符
	requestURL = e.sanitizeURL(requestURL)

	// 添加查询参数
	if len(reqConfig.Params) > 0 {
		u, err := url.Parse(requestURL)
		if err != nil {
			// 如果URL解析失败（可能包含特殊字符），尝试手动构建查询参数
			separator := "?"
			if strings.Contains(requestURL, "?") {
				separator = "&"
			}

			var params []string

			for key, value := range reqConfig.Params {
				// 替换参数值中的动态变量（如${random_number}）
				replacedValue := e.variableManager.ReplaceVariables(value)
				// 对参数进行URL编码
				params = append(params, url.QueryEscape(key)+"="+url.QueryEscape(replacedValue))
			}

			if len(params) > 0 {
				requestURL += separator + strings.Join(params, "&")
			}
		} else {
			q := u.Query()
			for key, value := range reqConfig.Params {
				// 替换参数值中的动态变量（如${random_number}）
				q.Add(key, e.variableManager.ReplaceVariables(value))
			}

			u.RawQuery = q.Encode()
			requestURL = u.String()
		}
	}

	return requestURL
}

// sanitizeURL 智能处理URL中的特殊字符
func (e *Executor) sanitizeURL(rawURL string) string {
	// 尝试解析URL
	_, err := url.Parse(rawURL)
	if err == nil {
		// URL解析成功，直接返回
		return rawURL
	}

	// URL解析失败，可能包含特殊字符，需要智能处理
	// 分离协议、主机和路径部分
	var scheme, host, path string

	// 提取协议
	if strings.HasPrefix(rawURL, "http://") {
		scheme = "http"
		rawURL = rawURL[7:]
	} else if strings.HasPrefix(rawURL, "https://") {
		scheme = "https"
		rawURL = rawURL[8:]
	} else {
		scheme = "http"
	}

	// 查找第一个斜杠，分离主机和路径
	slashIndex := strings.Index(rawURL, "/")
	if slashIndex == -1 {
		// 没有路径部分
		host = rawURL
		path = "/"
	} else {
		host = rawURL[:slashIndex]
		path = rawURL[slashIndex:]
	}

	// 对路径部分进行智能编码
	// 保留路径分隔符，但编码其他特殊字符
	pathParts := strings.Split(path, "/")
	for i, part := range pathParts {
		if part != "" {
			// 对路径段进行URL编码，但保留一些常见的安全字符
			pathParts[i] = e.encodePathSegment(part)
		}
	}

	encodedPath := strings.Join(pathParts, "/")

	// 重新构建URL
	return fmt.Sprintf("%s://%s%s", scheme, host, encodedPath)
}

// encodePathSegment 对URL路径段进行智能编码
func (e *Executor) encodePathSegment(segment string) string {
	// 定义需要编码的特殊字符
	needsEncoding := false

	for _, char := range segment {
		// 检查是否包含需要编码的字符
		if char < 32 || char > 126 ||
			char == ' ' || char == '"' || char == '#' || char == '%' ||
			char == '<' || char == '>' || char == '[' || char == ']' ||
			char == '{' || char == '}' || char == '|' || char == '\\' ||
			char == '^' || char == '`' || char == '@' {
			needsEncoding = true
			break
		}
	}

	if !needsEncoding {
		return segment
	}

	// 使用url.PathEscape进行编码，它会正确处理路径中的特殊字符
	return url.PathEscape(segment)
}

// executeAssertions 执行断言
func (e *Executor) executeAssertions(expected ExpectedResponse, response ResponseInfo) []AssertionResult {
	var results []AssertionResult

	// 状态码断言
	if expected.StatusCode > 0 {
		result := AssertionResult{
			Type:     "status_code",
			Field:    "status_code",
			Expected: expected.StatusCode,
			Actual:   response.StatusCode,
			Success:  response.StatusCode == expected.StatusCode,
			Message:  fmt.Sprintf("期望状态码 %d，实际状态码 %d", expected.StatusCode, response.StatusCode),
		}
		results = append(results, result)
	}

	// 响应头断言
	for key, expectedValue := range expected.Headers {
		// 对期望值进行变量替换
		replacedExpectedValue := e.variableManager.ReplaceVariables(expectedValue)

		actualValue := response.Headers[key]
		result := AssertionResult{
			Type:     "header",
			Field:    fmt.Sprintf("headers.%s", key),
			Expected: replacedExpectedValue,
			Actual:   actualValue,
			Success:  actualValue == replacedExpectedValue,
			Message:  fmt.Sprintf("期望响应头 %s: %s，实际值: %s", key, replacedExpectedValue, actualValue),
		}
		results = append(results, result)
	}

	// JSONPath断言
	for path, expectedValue := range expected.JSONPath {
		// 对期望值进行变量替换
		var replacedExpectedValue interface{} = expectedValue
		if expectedStr, ok := expectedValue.(string); ok {
			replacedExpectedValue = e.variableManager.ReplaceVariables(expectedStr)
		}

		actualValue := gjson.Get(response.Body, path)

		var actual interface{}

		if actualValue.Exists() {
			actual = actualValue.Value()
		}

		result := AssertionResult{
			Type:     "json_path",
			Field:    path,
			Expected: replacedExpectedValue,
			Actual:   actual,
			Success:  e.compareValues(replacedExpectedValue, actual),
			Message:  fmt.Sprintf("JSONPath %s 期望值: %v，实际值: %v", path, replacedExpectedValue, actual),
		}
		results = append(results, result)
	}

	// 自定义断言
	for _, assertion := range expected.Assertions {
		result := e.executeAssertion(assertion, response)
		results = append(results, result)
	}

	return results
}

// executeAssertion 执行单个断言
func (e *Executor) executeAssertion(assertion AssertionConfig, response ResponseInfo) AssertionResult {
	// 对断言的期望值进行变量替换
	expectedValue := assertion.Value
	if expectedStr, ok := assertion.Value.(string); ok {
		expectedValue = e.variableManager.ReplaceVariables(expectedStr)
	}

	result := AssertionResult{
		Type:     assertion.Type,
		Field:    assertion.Field,
		Expected: expectedValue,
		Optional: assertion.Optional,
		Message:  assertion.Message,
	}

	var actualValue interface{}

	var exists bool

	// 获取实际值
	if strings.HasPrefix(assertion.Field, "body.") {
		// JSON字段
		path := strings.TrimPrefix(assertion.Field, "body.")

		// 转换路径格式以兼容gjson
		path = e.convertPathForGjson(path)

		// 特殊处理 .length 字段
		if strings.HasSuffix(path, ".length") {
			// 获取数组字段，将.length转换为.#
			arrayPath := strings.TrimSuffix(path, ".length")

			jsonResult := gjson.Get(response.Body, arrayPath+".#")
			if jsonResult.Exists() {
				actualValue = int(jsonResult.Int())
				exists = true
			}
		} else {
			jsonResult := gjson.Get(response.Body, path)
			if jsonResult.Exists() {
				actualValue = jsonResult.Value()
				exists = true
			}
		}
	} else if strings.HasPrefix(assertion.Field, "headers.") {
		// 响应头字段
		headerKey := strings.TrimPrefix(assertion.Field, "headers.")
		if value, ok := response.Headers[headerKey]; ok {
			actualValue = value
			exists = true
		}
	} else if assertion.Field == "status_code" {
		actualValue = response.StatusCode
		exists = true
	} else if assertion.Field == "body" {
		// 对于type断言，需要解析JSON来获取实际类型
		if assertion.Type == "type" {
			jsonResult := gjson.Parse(response.Body)
			actualValue = jsonResult.Value()
		} else {
			actualValue = response.Body
		}

		exists = true
	}

	result.Actual = actualValue

	// 执行断言逻辑
	switch assertion.Type {
	case "equals":
		result.Success = e.compareValues(expectedValue, actualValue)
	case "not_equals":
		result.Success = !e.compareValues(expectedValue, actualValue)
	case "contains":
		if str, ok := actualValue.(string); ok {
			if expectedStr, ok := expectedValue.(string); ok {
				result.Success = strings.Contains(str, expectedStr)
			}
		}
	case "not_contains":
		if str, ok := actualValue.(string); ok {
			if expectedStr, ok := expectedValue.(string); ok {
				result.Success = !strings.Contains(str, expectedStr)
			}
		}
	case "regex":
		if str, ok := actualValue.(string); ok {
			if pattern, ok := expectedValue.(string); ok {
				if matched, err := regexp.MatchString(pattern, str); err == nil {
					result.Success = matched
				}
			}
		}
	case "exists":
		result.Success = exists
	case "not_exists":
		result.Success = !exists
	case "greater_than":
		result.Success = e.compareNumbers(actualValue, expectedValue, ">")
	case "less_than":
		result.Success = e.compareNumbers(actualValue, expectedValue, "<")
	case "greater_equal", "greater_than_or_equal":
		result.Success = e.compareNumbers(actualValue, expectedValue, ">=")
	case "less_equal", "less_than_or_equal":
		result.Success = e.compareNumbers(actualValue, expectedValue, "<=")
	case "type":
		result.Success = e.checkType(actualValue, expectedValue)
	case "starts_with":
		if str, ok := actualValue.(string); ok {
			if expectedStr, ok := expectedValue.(string); ok {
				result.Success = strings.HasPrefix(str, expectedStr)
			}
		}
	case "ends_with":
		if str, ok := actualValue.(string); ok {
			if expectedStr, ok := expectedValue.(string); ok {
				result.Success = strings.HasSuffix(str, expectedStr)
			}
		}
	case "empty":
		result.Success = e.isEmpty(actualValue)
	case "not_empty":
		result.Success = !e.isEmpty(actualValue)
	case "length":
		if expectedInt, ok := e.toInt(expectedValue); ok {
			result.Success = e.checkLength(actualValue, expectedInt, "==")
		}
	case "length_greater_than":
		if expectedInt, ok := e.toInt(expectedValue); ok {
			result.Success = e.checkLength(actualValue, expectedInt, ">")
		}
	case "length_less_than":
		if expectedInt, ok := e.toInt(expectedValue); ok {
			result.Success = e.checkLength(actualValue, expectedInt, "<")
		}
	case "length_greater_equal":
		if expectedInt, ok := e.toInt(expectedValue); ok {
			result.Success = e.checkLength(actualValue, expectedInt, ">=")
		}
	case "length_less_equal":
		if expectedInt, ok := e.toInt(expectedValue); ok {
			result.Success = e.checkLength(actualValue, expectedInt, "<=")
		}
	case "in":
		result.Success = e.checkInList(actualValue, expectedValue)
	case "not_in":
		result.Success = !e.checkInList(actualValue, expectedValue)
	}

	if result.Message == "" {
		result.Message = fmt.Sprintf("%s 断言失败: 期望 %v，实际 %v", assertion.Type, expectedValue, actualValue)
	}

	return result
}

// compareValues 比较两个值是否相等
func (e *Executor) compareValues(expected, actual interface{}) bool {
	if expected == nil && actual == nil {
		return true
	}

	if expected == nil || actual == nil {
		return false
	}

	// 首先尝试直接比较
	if expected == actual {
		return true
	}

	// 尝试数字比较
	if e.tryNumericComparison(expected, actual) {
		return true
	}

	// 最后尝试字符串比较
	expectedStr := fmt.Sprintf("%v", expected)
	actualStr := fmt.Sprintf("%v", actual)

	return expectedStr == actualStr
}

// tryNumericComparison 尝试数字比较
func (e *Executor) tryNumericComparison(expected, actual interface{}) bool {
	expectedFloat, err1 := e.toFloat64(expected)
	actualFloat, err2 := e.toFloat64(actual)

	if err1 == nil && err2 == nil {
		return expectedFloat == actualFloat
	}

	return false
}

// compareNumbers 比较数字
func (e *Executor) compareNumbers(actual, expected interface{}, operator string) bool {
	actualFloat, err1 := e.toFloat64(actual)
	expectedFloat, err2 := e.toFloat64(expected)

	if err1 != nil || err2 != nil {
		return false
	}

	switch operator {
	case ">":
		return actualFloat > expectedFloat
	case "<":
		return actualFloat < expectedFloat
	case ">=":
		return actualFloat >= expectedFloat
	case "<=":
		return actualFloat <= expectedFloat
	default:
		return false
	}
}

// toFloat64 将interface{}转换为float64
func (e *Executor) toFloat64(value interface{}) (float64, error) {
	switch v := value.(type) {
	case float64:
		return v, nil
	case float32:
		return float64(v), nil
	case int:
		return float64(v), nil
	case int64:
		return float64(v), nil
	case string:
		return strconv.ParseFloat(v, 64)
	default:
		return 0, fmt.Errorf("无法转换为数字: %v", value)
	}
}

// checkType 检查值的类型
func (e *Executor) checkType(actualValue interface{}, expectedType interface{}) bool {
	if actualValue == nil {
		return expectedType == "null" || expectedType == nil
	}

	expectedTypeStr, ok := expectedType.(string)
	if !ok {
		return false
	}

	actualType := e.getValueType(actualValue)

	return actualType == expectedTypeStr
}

// getValueType 获取值的类型字符串
func (e *Executor) getValueType(value interface{}) string {
	if value == nil {
		return "null"
	}

	switch value.(type) {
	case string:
		return "string"
	case int, int8, int16, int32, int64:
		return "number" // 统一返回number，因为JSON中的数字都是number类型
	case float32, float64:
		return "number" // 统一返回number，不区分整数和浮点数
	case bool:
		return "boolean"
	case []interface{}:
		return "array"
	case map[string]interface{}:
		return "object"
	default:
		// 尝试通过反射获取更精确的类型
		switch fmt.Sprintf("%T", value) {
		case "json.Number":
			return "number" // JSON数字统一返回number
		default:
			return "unknown"
		}
	}
}

// isEmpty 检查值是否为空
func (e *Executor) isEmpty(value interface{}) bool {
	if value == nil {
		return true
	}

	switch v := value.(type) {
	case string:
		return v == ""
	case []interface{}:
		return len(v) == 0
	case map[string]interface{}:
		return len(v) == 0
	case int, int8, int16, int32, int64:
		return v == 0
	case float32, float64:
		return v == 0
	case bool:
		return !v
	default:
		// 尝试转换为字符串检查
		str := fmt.Sprintf("%v", value)
		return str == "" || str == "0" || str == "false" || str == "<nil>"
	}
}

// toInt 将interface{}转换为int
func (e *Executor) toInt(value interface{}) (int, bool) {
	switch v := value.(type) {
	case int:
		return v, true
	case int8:
		return int(v), true
	case int16:
		return int(v), true
	case int32:
		return int(v), true
	case int64:
		return int(v), true
	case float32:
		return int(v), true
	case float64:
		return int(v), true
	case string:
		if i, err := strconv.Atoi(v); err == nil {
			return i, true
		}
	}

	return 0, false
}

// checkLength 检查值的长度
func (e *Executor) checkLength(value interface{}, expectedLength int, operator string) bool {
	var actualLength int

	switch v := value.(type) {
	case string:
		actualLength = len(v)
	case []interface{}:
		actualLength = len(v)
	case map[string]interface{}:
		actualLength = len(v)
	default:
		// 尝试转换为字符串获取长度
		str := fmt.Sprintf("%v", value)
		actualLength = len(str)
	}

	switch operator {
	case "==":
		return actualLength == expectedLength
	case ">":
		return actualLength > expectedLength
	case "<":
		return actualLength < expectedLength
	case ">=":
		return actualLength >= expectedLength
	case "<=":
		return actualLength <= expectedLength
	default:
		return false
	}
}

// checkInList 检查值是否在列表中
func (e *Executor) checkInList(value interface{}, expectedList interface{}) bool {
	// 期望值应该是一个数组
	list, ok := expectedList.([]interface{})
	if !ok {
		// 尝试解析字符串形式的数组
		if listStr, ok := expectedList.(string); ok {
			var parsedList []interface{}
			if err := json.Unmarshal([]byte(listStr), &parsedList); err == nil {
				list = parsedList
			} else {
				return false
			}
		} else {
			return false
		}
	}

	// 检查值是否在列表中
	for _, item := range list {
		if e.compareValues(value, item) {
			return true
		}
	}

	return false
}

// convertPathForGjson 转换路径格式以兼容gjson
// 将 entries[0].obj_type 转换为 entries.0.obj_type
// 将 entries.length 转换为 entries.#
func (e *Executor) convertPathForGjson(path string) string {
	// 使用正则表达式将 [数字] 转换为 .数字
	re := regexp.MustCompile(`\[(\d+)\]`)
	path = re.ReplaceAllString(path, ".$1")

	// 将 .length 转换为 .#
	path = strings.ReplaceAll(path, ".length", ".#")

	return path
}
