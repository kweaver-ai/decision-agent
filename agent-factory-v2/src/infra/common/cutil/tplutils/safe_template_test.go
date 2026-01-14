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
