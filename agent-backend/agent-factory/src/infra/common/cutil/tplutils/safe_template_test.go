package tplutils

import (
	"testing"
)

func TestSafeRenderTemplate(t *testing.T) {
	tests := []struct {
		name     string
		template string
		data     map[string]interface{}
		expected string
		wantErr  bool
	}{
		{
			name:     "完整的深层嵌套",
			template: "用户{{.User.Info.Basic.Name}}(ID:{{.User.Info.Basic.ID}})的联系方式是：{{.User.Info.Contact.Email}}，居住在{{.User.Info.Address.City}}市{{.User.Info.Address.Street}}",
			data: map[string]interface{}{
				"User": map[string]interface{}{
					"Info": map[string]interface{}{
						"Basic": map[string]interface{}{
							"Name": "张三",
							"ID":   "12345",
						},
						"Contact": map[string]interface{}{
							"Email": "zhangsan@example.com",
							"Phone": "13800138000",
						},
						"Address": map[string]interface{}{
							"City":   "北京",
							"Street": "长安街",
							"ZIP":    "100000",
						},
					},
				},
			},
			expected: "用户张三(ID:12345)的联系方式是：zhangsan@example.com，居住在北京市长安街",
			wantErr:  false,
		},
		{
			name:     "完全缺失变量",
			template: "{{.User.Name}} - {{.User.Age}}岁",
			data: map[string]interface{}{
				"Other": "其他数据",
			},
			expected: "{{.User.Name}} - {{.User.Age}}岁",
			wantErr:  false,
		},
		{
			name:     "部分缺失变量",
			template: "{{.User.Name}} - {{.User.Age}}岁",
			data: map[string]interface{}{
				"User": map[string]interface{}{
					"Name": "张三",
					// Age 缺失
				},
			},
			expected: "张三 - {{.User.Age}}岁",
			wantErr:  false,
		},
		{
			name:     "嵌套结构不完整",
			template: "{{.User.Info.Age}}岁",
			data: map[string]interface{}{
				"User": map[string]interface{}{
					"Name": "张三",
					// Info 整个结构缺失
				},
			},
			expected: "{{.User.Info.Age}}岁",
			wantErr:  false,
		},
		{
			name:     "my",
			template: "根据用户{{.params.user_department}}推荐相关文档",
			data: map[string]interface{}{
				"params": map[string]interface{}{
					"user_department": "技术部",
				},
			},
			expected: "根据用户技术部推荐相关文档",
			wantErr:  false,
		},
		{
			name:     "空值处理",
			template: "用户名: {{.User.Name}}, 年龄: {{.User.Age}}",
			data: map[string]interface{}{
				"User": map[string]interface{}{
					"Name": "",  // 空字符串
					"Age":  nil, // nil值
				},
			},
			expected: "用户名: , 年龄: {{.User.Age}}",
			wantErr:  false,
		},
		{
			name: "多行模板",
			template: `用户信息：
姓名：{{.User.Name}}
年龄：{{.User.Age}}
邮箱：{{.User.Email}}
电话：{{.User.Phone}}`,
			data: map[string]interface{}{
				"User": map[string]interface{}{
					"Name":  "王五",
					"Phone": "98765432",
					// Age 和 Email 缺失
				},
			},
			expected: `用户信息：
姓名：王五
年龄：{{.User.Age}}
邮箱：{{.User.Email}}
电话：98765432`,
			wantErr: false,
		},
		{
			name:     "特殊字符",
			template: "{{.User.Name}}!@#$%^&*{{.User.Age}}",
			data: map[string]interface{}{
				"User": map[string]interface{}{
					"Name": "<script>alert('test')</script>",
					// Age 缺失
				},
			},
			// json序列化后的结果
			expected: `\u003cscript\u003ealert('test')\u003c/script\u003e!@#$%^&*{{.User.Age}}`,
			wantErr:  false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := SafeRenderTemplate(tt.template, tt.data)

			// 检查错误
			if (err != nil) != tt.wantErr {
				t.Errorf("SafeRenderTemplate() error = %v, wantErr %v", err, tt.wantErr)
				return
			}

			// 检查结果
			if result != tt.expected {
				t.Errorf("SafeRenderTemplate() = %v, want %v", result, tt.expected)
			} else {
				t.Logf("测试通过，结果: %v", result)
			}
		})
	}
}

func TestSafeRenderTemplate_EdgeCases(t *testing.T) {
	tests := []struct {
		name     string
		template string
		data     map[string]interface{}
		expected string
	}{
		{
			name:     "空模板",
			template: "",
			data:     map[string]interface{}{},
			expected: "",
		},
		{
			name:     "纯文本模板",
			template: "Hello World",
			data:     map[string]interface{}{},
			expected: "Hello World",
		},
		{
			name:     "连续的占位符",
			template: "{{.A}}{{.B}}{{.C}}",
			data: map[string]interface{}{
				"A": "1",
				"B": "2",
				"C": "3",
			},
			expected: "123",
		},
		{
			name:     "没有占位符的模板",
			template: "Just plain text",
			data: map[string]interface{}{
				"User": map[string]interface{}{
					"Name": "张三",
				},
			},
			expected: "Just plain text",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := SafeRenderTemplate(tt.template, tt.data)
			if err != nil {
				t.Errorf("SafeRenderTemplate() unexpected error = %v", err)
			}
			if result != tt.expected {
				t.Errorf("SafeRenderTemplate() = %v, want %v", result, tt.expected)
			}
		})
	}
}

// 测试 SafeGet 函数
func TestSafeGet(t *testing.T) {
	data := map[string]interface{}{
		"User": map[string]interface{}{
			"Name": "张三",
			"Info": map[string]interface{}{
				"Age": 25,
			},
		},
	}

	tests := []struct {
		name     string
		path     string
		expected interface{}
	}{
		{
			name:     "获取存在的值",
			path:     "User.Name",
			expected: "张三",
		},
		{
			name:     "获取嵌套值",
			path:     "User.Info.Age",
			expected: 25,
		},
		{
			name:     "获取不存在的值",
			path:     "User.NotExist",
			expected: nil,
		},
		{
			name:     "获取不存在的嵌套值",
			path:     "User.Info.NotExist",
			expected: nil,
		},
		{
			name:     "完全不存在的路径",
			path:     "NotExist.Something",
			expected: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := SafeGet(data, tt.path)
			if result != tt.expected {
				t.Errorf("SafeGet() = %v, want %v", result, tt.expected)
			} else {
				t.Logf("测试通过，结果: %v", result)
			}
		})
	}
}

// Test SafeGet with nil data
func TestSafeGet_NilData(t *testing.T) {
	result := SafeGet(nil, "User.Name")
	if result != nil {
		t.Errorf("SafeGet() with nil data = %v, want nil", result)
	}
}

// Test SafeGet with non-map intermediate value
func TestSafeGet_NonMapIntermediate(t *testing.T) {
	data := map[string]interface{}{
		"User": "string value", // Not a map
	}

	result := SafeGet(data, "User.Name")
	if result != nil {
		t.Errorf("SafeGet() with non-map intermediate = %v, want nil", result)
	}
}

// Test SafeGet with empty path
func TestSafeGet_EmptyPath(t *testing.T) {
	data := map[string]interface{}{
		"User": "张三",
	}

	result := SafeGet(data, "")
	// Empty path returns nil because strings.Split("", ".") returns [""]
	// and there's no key "" in the map
	if result != nil {
		t.Errorf("SafeGet() with empty path = %v, want nil", result)
	}
}

// Test SafeRenderTemplate with nil value in data
func TestSafeRenderTemplate_NilValue(t *testing.T) {
	template := "用户: {{.User.Name}}"
	data := map[string]interface{}{
		"User": map[string]interface{}{
			"Name": nil,
		},
	}

	result, err := SafeRenderTemplate(template, data)
	if err != nil {
		t.Errorf("SafeRenderTemplate() unexpected error = %v", err)
	}
	// Should preserve placeholder for nil value
	if result != "用户: {{.User.Name}}" {
		t.Errorf("SafeRenderTemplate() with nil value = %v, want '用户: {{.User.Name}}'", result)
	}
}

// Test SafeRenderTemplate with template that has no closing brace after dot
func TestSafeRenderTemplate_MalformedTemplate(t *testing.T) {
	// SafeRenderTemplate converts {{.xxx}} to {{safe "xxx"}} before parsing
	// So {{.User.Name gets converted to {{safe "User.Name}} which is valid
	// The missing brace becomes part of the rest string
	template := "Hello {{.User.Name"
	data := map[string]interface{}{
		"User": map[string]interface{}{
			"Name": "张三",
		},
	}

	result, err := SafeRenderTemplate(template, data)
	// This should succeed and render what it can
	if err != nil {
		t.Errorf("SafeRenderTemplate() unexpected error = %v", err)
	}
	// The rest "}}" after processing becomes part of output
	t.Logf("Result: %s", result)
}
