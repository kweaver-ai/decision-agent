package cutil

import (
	"os"
	"testing"
)

func TestGetEnv(t *testing.T) {
	key := "TEST_KEY"
	defaultValue := "default"

	// 测试环境变量存在的情况
	os.Setenv(key, "value")

	if val := GetEnv(key, defaultValue); val != "value" {
		t.Errorf("Expected 'value', but got %s", val)
	}

	// 测试环境变量不存在的情况
	os.Unsetenv(key)

	if val := GetEnv(key, defaultValue); val != defaultValue {
		t.Errorf("Expected '%s', but got %s", defaultValue, val)
	}
}

func TestGetEnvMustInt(t *testing.T) {
	key := "TEST_INT_KEY"
	defaultValue := 42

	// 测试环境变量存在且为可转换整数的情况
	os.Setenv(key, "123")

	if val := GetEnvMustInt(key, defaultValue); val != 123 {
		t.Errorf("Expected 123, but got %d", val)
	}

	// 测试环境变量存在但不可转换为整数的情况，预期出现panic
	os.Setenv(key, "abc")

	defer func() {
		if r := recover(); r == nil {
			t.Errorf("Expected panic for non-integer value")
		}
	}()
	GetEnvMustInt(key, defaultValue)

	// 测试环境变量不存在的情况
	os.Unsetenv(key)

	if val := GetEnvMustInt(key, defaultValue); val != defaultValue {
		t.Errorf("Expected %d, but got %d", defaultValue, val)
	}
}
