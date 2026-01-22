package apitest

import (
	"crypto/rand"
	"fmt"
	"math/big"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/google/uuid"
	"github.com/tidwall/gjson"
)

// VariableManager 变量管理器
type VariableManager struct {
	variables map[string]string
	config    VariableConfig
}

// VariableConfig 变量配置
type VariableConfig struct {
	RandomNumberMin    int `json:"random_number_min" yaml:"random_number_min"`       // 随机数最小值
	RandomNumberMax    int `json:"random_number_max" yaml:"random_number_max"`       // 随机数最大值
	RandomStringLength int `json:"random_string_length" yaml:"random_string_length"` // 随机字符串长度
	RandomNameLength   int `json:"random_name_length" yaml:"random_name_length"`     // 随机姓名长度
}

// VariableExtraction 变量提取配置
type VariableExtraction struct {
	Name    string `json:"name" yaml:"name"`       // 变量名
	Source  string `json:"source" yaml:"source"`   // 提取源: body, header, status_code
	Path    string `json:"path" yaml:"path"`       // JSONPath或字段路径
	Regex   string `json:"regex" yaml:"regex"`     // 正则表达式提取
	Default string `json:"default" yaml:"default"` // 默认值
}

// NewVariableManager 创建变量管理器
func NewVariableManager() *VariableManager {
	return &VariableManager{
		variables: make(map[string]string),
		config: VariableConfig{
			RandomNumberMin:    1,
			RandomNumberMax:    1000,
			RandomStringLength: 10,
			RandomNameLength:   8,
		},
	}
}

// NewVariableManagerWithConfig 使用配置创建变量管理器
func NewVariableManagerWithConfig(config VariableConfig) *VariableManager {
	vm := NewVariableManager()
	vm.config = config

	return vm
}

// SetVariable 设置变量
func (vm *VariableManager) SetVariable(name, value string) {
	vm.variables[name] = value
}

// GetVariable 获取变量
func (vm *VariableManager) GetVariable(name string) (string, bool) {
	value, exists := vm.variables[name]
	return value, exists
}

// SetVariables 批量设置变量
func (vm *VariableManager) SetVariables(variables map[string]string) {
	for name, value := range variables {
		vm.variables[name] = value
	}
}

// GetAllVariables 获取所有变量
func (vm *VariableManager) GetAllVariables() map[string]string {
	result := make(map[string]string)
	for k, v := range vm.variables {
		result[k] = v
	}

	return result
}

// ReplaceVariables 替换文本中的变量
func (vm *VariableManager) ReplaceVariables(text string) string {
	result := text

	// 替换动态变量
	result = vm.replaceDynamicVariables(result)

	// 替换用户定义的变量
	for name, value := range vm.variables {
		placeholder := fmt.Sprintf("{{%s}}", name)
		result = strings.ReplaceAll(result, placeholder, value)
	}

	return result
}

// replaceDynamicVariables 替换动态变量
func (vm *VariableManager) replaceDynamicVariables(text string) string {
	result := text

	// UUID变量
	uuidRegex := regexp.MustCompile(`\$\{uuid\}`)
	for uuidRegex.MatchString(result) {
		result = uuidRegex.ReplaceAllString(result, uuid.New().String())
	}

	// 时间戳变量
	timestampRegex := regexp.MustCompile(`\$\{timestamp\}`)
	for timestampRegex.MatchString(result) {
		result = timestampRegex.ReplaceAllString(result, strconv.FormatInt(time.Now().Unix(), 10))
	}

	// 毫秒时间戳变量
	timestampMsRegex := regexp.MustCompile(`\$\{timestamp_ms\}`)
	for timestampMsRegex.MatchString(result) {
		result = timestampMsRegex.ReplaceAllString(result, strconv.FormatInt(time.Now().UnixMilli(), 10))
	}

	// 随机数变量 - 支持范围设置
	randomNumberRegex := regexp.MustCompile(`\$\{random_number(?::(\d+)-(\d+))?\}`)

	matches := randomNumberRegex.FindAllStringSubmatch(result, -1)
	for _, match := range matches {
		min := vm.config.RandomNumberMin
		max := vm.config.RandomNumberMax

		if len(match) > 2 && match[1] != "" && match[2] != "" {
			if parsedMin, err := strconv.Atoi(match[1]); err == nil {
				min = parsedMin
			}

			if parsedMax, err := strconv.Atoi(match[2]); err == nil {
				max = parsedMax
			}
		}

		randomNum := vm.generateRandomNumber(min, max)
		result = strings.Replace(result, match[0], strconv.Itoa(randomNum), 1)
	}

	// 随机字符串变量 - 支持长度设置
	randomStringRegex := regexp.MustCompile(`\$\{random_string(?::(\d+))?\}`)

	matches = randomStringRegex.FindAllStringSubmatch(result, -1)
	for _, match := range matches {
		length := vm.config.RandomStringLength

		if len(match) > 1 && match[1] != "" {
			if parsedLength, err := strconv.Atoi(match[1]); err == nil {
				length = parsedLength
			}
		}

		randomStr := vm.generateRandomString(length)
		result = strings.Replace(result, match[0], randomStr, 1)
	}

	// 随机姓名变量 - 支持长度设置
	randomNameRegex := regexp.MustCompile(`\$\{random_name(?::(\d+))?\}`)

	matches = randomNameRegex.FindAllStringSubmatch(result, -1)
	for _, match := range matches {
		length := vm.config.RandomNameLength

		if len(match) > 1 && match[1] != "" {
			if parsedLength, err := strconv.Atoi(match[1]); err == nil {
				length = parsedLength
			}
		}

		randomName := vm.generateRandomName(length)
		result = strings.Replace(result, match[0], randomName, 1)
	}

	return result
}

// generateRandomNumber 生成指定范围的随机数
func (vm *VariableManager) generateRandomNumber(min, max int) int {
	if min >= max {
		return min
	}

	diff := max - min

	n, err := rand.Int(rand.Reader, big.NewInt(int64(diff)))
	if err != nil {
		return min
	}

	return min + int(n.Int64())
}

// generateRandomString 生成指定长度的随机字符串
func (vm *VariableManager) generateRandomString(length int) string {
	const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

	result := make([]byte, length)

	for i := range result {
		n, err := rand.Int(rand.Reader, big.NewInt(int64(len(charset))))
		if err != nil {
			result[i] = charset[0]
		} else {
			result[i] = charset[n.Int64()]
		}
	}

	return string(result)
}

// generateRandomName 生成指定长度的随机姓名
func (vm *VariableManager) generateRandomName(length int) string {
	// 常见的姓名字符，包含中英文
	firstNames := []string{"张", "李", "王", "刘", "陈", "杨", "赵", "黄", "周", "吴", "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗"}
	lastNames := []string{"伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "军", "洋", "勇", "艳", "杰", "娟", "涛", "明", "超", "秀兰", "霞"}

	if length <= 2 {
		// 生成中文姓名
		firstIdx := vm.generateRandomNumber(0, len(firstNames))
		lastIdx := vm.generateRandomNumber(0, len(lastNames))

		return firstNames[firstIdx] + lastNames[lastIdx]
	} else {
		// 生成英文姓名
		const nameChars = "abcdefghijklmnopqrstuvwxyz"

		result := make([]byte, length)

		// 首字母大写
		n, err := rand.Int(rand.Reader, big.NewInt(int64(len(nameChars))))
		if err != nil {
			result[0] = 'A'
		} else {
			result[0] = nameChars[n.Int64()] - 32 // 转为大写
		}

		// 其余字母小写
		for i := 1; i < length; i++ {
			n, err := rand.Int(rand.Reader, big.NewInt(int64(len(nameChars))))
			if err != nil {
				result[i] = 'a'
			} else {
				result[i] = nameChars[n.Int64()]
			}
		}

		return string(result)
	}
}

// ExtractVariables 从响应中提取变量
func (vm *VariableManager) ExtractVariables(extractions []VariableExtraction, response ResponseInfo) error {
	for _, extraction := range extractions {
		value, err := vm.extractValue(extraction, response)
		if err != nil {
			if extraction.Default != "" {
				value = extraction.Default
			} else {
				continue // 跳过提取失败的变量
			}
		}

		vm.SetVariable(extraction.Name, value)
	}

	return nil
}

// extractValue 从响应中提取单个值
func (vm *VariableManager) extractValue(extraction VariableExtraction, response ResponseInfo) (string, error) {
	var sourceValue string

	switch extraction.Source {
	case "body":
		sourceValue = response.Body
	case "status_code":
		sourceValue = strconv.Itoa(response.StatusCode)
	case "header":
		if headerValue, exists := response.Headers[extraction.Path]; exists {
			sourceValue = headerValue
		} else {
			return "", fmt.Errorf("header %s not found", extraction.Path)
		}
	default:
		return "", fmt.Errorf("unsupported source: %s", extraction.Source)
	}

	// 如果指定了正则表达式，使用正则提取
	if extraction.Regex != "" {
		regex, err := regexp.Compile(extraction.Regex)
		if err != nil {
			return "", fmt.Errorf("invalid regex: %s", extraction.Regex)
		}

		matches := regex.FindStringSubmatch(sourceValue)
		if len(matches) > 1 {
			return matches[1], nil // 返回第一个捕获组
		} else if len(matches) > 0 {
			return matches[0], nil // 返回整个匹配
		} else {
			return "", fmt.Errorf("regex pattern not matched")
		}
	}

	// 如果是body且指定了JSONPath，使用JSONPath提取
	if extraction.Source == "body" && extraction.Path != "" {
		// 转换路径格式以兼容gjson
		path := vm.convertPathForGjson(extraction.Path)

		result := gjson.Get(sourceValue, path)
		if result.Exists() {
			// 确保所有类型的值都转换为字符串
			switch result.Type {
			case gjson.String:
				return result.String(), nil
			case gjson.Number:
				return result.String(), nil
			case gjson.True:
				return "true", nil
			case gjson.False:
				return "false", nil
			case gjson.Null:
				return "null", nil
			default:
				// 对于复杂类型（数组、对象），返回JSON字符串
				return result.Raw, nil
			}
		} else {
			return "", fmt.Errorf("JSONPath %s not found (converted to %s)", extraction.Path, path)
		}
	}

	// 直接返回源值
	return sourceValue, nil
}

// ClearVariables 清空所有变量
func (vm *VariableManager) ClearVariables() {
	vm.variables = make(map[string]string)
}

// GetVariableCount 获取变量数量
func (vm *VariableManager) GetVariableCount() int {
	return len(vm.variables)
}

// convertPathForGjson 转换路径格式以兼容gjson
// 将 entries[0].obj_type 转换为 entries.0.obj_type
// 将 entries.length 转换为 entries.#
func (vm *VariableManager) convertPathForGjson(path string) string {
	// 使用正则表达式将 [数字] 转换为 .数字
	re := regexp.MustCompile(`\[(\d+)\]`)
	path = re.ReplaceAllString(path, ".$1")

	// 将 .length 转换为 .#
	path = strings.ReplaceAll(path, ".length", ".#")

	return path
}
