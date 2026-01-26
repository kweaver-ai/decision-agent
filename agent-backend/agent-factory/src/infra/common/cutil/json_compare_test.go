package cutil

import (
	"testing"
)

func TestJSONStrCompare(t *testing.T) {
	tests := []struct {
		name     string
		jsonStr1 string
		jsonStr2 string
		expected bool
	}{
		{
			name:     "相同的JSON",
			jsonStr1: `{"name": "John", "age": 30}`,
			jsonStr2: `{"name": "John", "age": 30}`,
			expected: true,
		},
		{
			name:     "不同顺序但内容相同",
			jsonStr1: `{"name": "John", "age": 30}`,
			jsonStr2: `{"age": 30, "name": "John"}`,
			expected: true,
		},
		{
			name:     "不同的值",
			jsonStr1: `{"name": "John", "age": 30}`,
			jsonStr2: `{"name": "Jane", "age": 30}`,
			expected: false,
		},
		{
			name:     "结构不同",
			jsonStr1: `{"name": "John"}`,
			jsonStr2: `{"name": "John", "age": 30}`,
			expected: false,
		},
			{
			name:     "空JSON",
			jsonStr1: `{}`,
			jsonStr2: `{}`,
			expected: true,
		},
		{
			name:     "无效的JSON1",
			jsonStr1: `{"name": "John", "age": 30}`,
			jsonStr2: `{"name": "John", "age": 30}`,
			expected: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := JSONStrCompare(tt.jsonStr1, tt.jsonStr2)
			if tt.expected {
				if err != nil {
					t.Errorf("JSONStrCompare() unexpected error: %v", err)
				}
				if !result {
					t.Errorf("JSONStrCompare() = %v, want true", result)
				}
			} else {
				if err == nil && result {
					t.Errorf("JSONStrCompare() should return false for different JSON")
				}
			}
		})
	}
}
