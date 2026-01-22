package cutil

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestIsStringOrNumber(t *testing.T) {
	t.Parallel()

	// 测试字符串
	var value interface{} = "a"

	assert.Equal(t, true, IsStringOrNumber(value), "IsStringOrNumber failed")

	// 测试int
	value = 1
	assert.Equal(t, true, IsStringOrNumber(value), "IsStringOrNumber failed")

	// 测试uint
	value = uint(1)
	assert.Equal(t, true, IsStringOrNumber(value), "IsStringOrNumber failed")

	// 测试float
	value = float32(1.1)
	assert.Equal(t, true, IsStringOrNumber(value), "IsStringOrNumber failed")

	// 测试其他类型
	value = struct{}{}
	assert.Equal(t, false, IsStringOrNumber(value), "IsStringOrNumber failed")

	// 测试其他类型
	value = []string{"a"}
	assert.Equal(t, false, IsStringOrNumber(value), "IsStringOrNumber failed")

	// 测试其他类型

	value = map[string]interface{}{"a": "b"}
	assert.Equal(t, false, IsStringOrNumber(value), "IsStringOrNumber failed")
}
