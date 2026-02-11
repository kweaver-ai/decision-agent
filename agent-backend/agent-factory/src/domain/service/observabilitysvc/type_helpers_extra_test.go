package observabilitysvc

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/agentrespvo"
	"github.com/stretchr/testify/assert"
)

// TestSafeGetString_NilMap tests safeGetString with nil map
func TestSafeGetString_NilMap(t *testing.T) {
	result := safeGetString(nil, "key")
	assert.Equal(t, "", result)
}

// TestSafeGetString_EmptyKey tests safeGetString with empty key
func TestSafeGetString_EmptyKey(t *testing.T) {
	m := map[string]any{"": "value"}
	result := safeGetString(m, "")
	assert.Equal(t, "value", result)
}

// TestSafeGetBool_NilMap tests safeGetBool with nil map
func TestSafeGetBool_NilMap(t *testing.T) {
	result := safeGetBool(nil, "key")
	assert.Equal(t, false, result)
}

// TestSafeGetFloat64_NilMap tests safeGetFloat64 with nil map
func TestSafeGetFloat64_NilMap(t *testing.T) {
	result := safeGetFloat64(nil, "key")
	assert.Equal(t, 0.0, result)
}

// TestSafeGetFloat64_NegativeValue tests safeGetFloat64 with negative value
func TestSafeGetFloat64_NegativeValue(t *testing.T) {
	m := map[string]any{"key": -123.45}
	result := safeGetFloat64(m, "key")
	assert.Equal(t, -123.45, result)
}

// TestSafeGetInt64_NilMap tests safeGetInt64 with nil map
func TestSafeGetInt64_NilMap(t *testing.T) {
	result := safeGetInt64(nil, "key")
	assert.Equal(t, int64(0), result)
}

// TestSafeGetInt64_NegativeFloat tests safeGetInt64 with negative float
func TestSafeGetInt64_NegativeFloat(t *testing.T) {
	m := map[string]any{"key": -456.78}
	result := safeGetInt64(m, "key")
	assert.Equal(t, int64(-456), result)
}

// TestSafeGetInt64_LargeFloat tests safeGetInt64 with large float value
func TestSafeGetInt64_LargeFloat(t *testing.T) {
	m := map[string]any{"key": 9007199254740991.0}
	result := safeGetInt64(m, "key")
	// The function returns the float value converted to int64
	assert.Equal(t, int64(9007199254740991), result)
}

// TestSafeParseSkillInfo_NilData tests safeParseSkillInfo with nil data
func TestSafeParseSkillInfo_NilData(t *testing.T) {
	result := safeParseSkillInfo(nil)
	assert.Nil(t, result)
}

// TestSafeParseSkillInfo_EmptyMap tests safeParseSkillInfo with empty map
func TestSafeParseSkillInfo_EmptyMap(t *testing.T) {
	data := map[string]any{}
	result := safeParseSkillInfo(data)
	assert.NotNil(t, result)
	assert.Equal(t, "", result.Type)
	assert.Equal(t, "", result.Name)
	assert.False(t, result.Checked)
	assert.Nil(t, result.Args)
}

// TestSafeParseSkillInfo_NoArgs tests safeParseSkillInfo without args
func TestSafeParseSkillInfo_NoArgs(t *testing.T) {
	data := map[string]any{
		"type": "tool",
		"name": "test_tool",
	}
	result := safeParseSkillInfo(data)
	assert.NotNil(t, result)
	assert.Equal(t, "tool", result.Type)
	assert.Equal(t, "test_tool", result.Name)
	assert.Nil(t, result.Args)
}

// TestSafeParseArgs_NilData tests safeParseArgs with nil data
func TestSafeParseArgs_NilData(t *testing.T) {
	result := safeParseArgs(nil)
	assert.Nil(t, result)
}

// TestSafeParseArgs_EmptyArray tests safeParseArgs with empty array
func TestSafeParseArgs_EmptyArray(t *testing.T) {
	result := safeParseArgs([]any{})
	assert.Nil(t, result)
}

// TestSafeParseArgs_SingleArg tests safeParseArgs with single argument
func TestSafeParseArgs_SingleArg(t *testing.T) {
	data := []any{
		map[string]any{
			"name":  "param1",
			"value": "value1",
			"type":  "string",
		},
	}
	result := safeParseArgs(data)
	assert.NotNil(t, result)
	assert.Len(t, result, 1)
	assert.Equal(t, "param1", result[0].Name)
	assert.Equal(t, "value1", result[0].Value)
	assert.Equal(t, "string", result[0].Type)
}

// TestSafeParseArgs_ArgsWithoutValue tests safeParseArgs with args without value field
func TestSafeParseArgs_ArgsWithoutValue(t *testing.T) {
	data := []any{
		map[string]any{
			"name": "param1",
			"type": "string",
		},
	}
	result := safeParseArgs(data)
	assert.NotNil(t, result)
	assert.Len(t, result, 1)
	assert.Equal(t, "param1", result[0].Name)
	assert.Nil(t, result[0].Value)
}

// TestSafeParseArgs_NonArrayData tests safeParseArgs with non-array data
func TestSafeParseArgs_NonArrayData(t *testing.T) {
	result := safeParseArgs("string")
	assert.Nil(t, result)
}

// TestSafeParseTokenUsage_NilData tests safeParseTokenUsage with nil data
func TestSafeParseTokenUsage_NilData(t *testing.T) {
	result := safeParseTokenUsage(nil)
	assert.Equal(t, agentrespvo.TokenUsage{}, result)
}

// TestSafeParseTokenUsage_EmptyMap tests safeParseTokenUsage with empty map
func TestSafeParseTokenUsage_EmptyMap(t *testing.T) {
	data := map[string]any{}
	result := safeParseTokenUsage(data)
	assert.Equal(t, agentrespvo.TokenUsage{}, result)
}

// TestSafeParseTokenUsage_PartialData tests safeParseTokenUsage with partial data
func TestSafeParseTokenUsage_PartialData(t *testing.T) {
	data := map[string]any{
		"prompt_tokens": 100.0,
	}
	result := safeParseTokenUsage(data)
	assert.Equal(t, int64(100), result.PromptTokens)
	assert.Equal(t, int64(0), result.CompletionTokens)
	assert.Equal(t, int64(0), result.TotalTokens)
}

// TestSafeParseTokenUsage_WithPromptDetails tests safeParseTokenUsage with prompt token details
func TestSafeParseTokenUsage_WithPromptDetails(t *testing.T) {
	data := map[string]any{
		"prompt_tokens":     100.0,
		"completion_tokens": 50.0,
		"total_tokens":      150.0,
		"prompt_tokens_details": map[string]any{
			"cached_tokens":   30.0,
			"uncached_tokens": 70.0,
		},
	}
	result := safeParseTokenUsage(data)
	assert.Equal(t, int64(100), result.PromptTokens)
	assert.Equal(t, int64(50), result.CompletionTokens)
	assert.Equal(t, int64(150), result.TotalTokens)
	assert.Equal(t, int64(30), result.PromptTokenDetails.CachedTokens)
	assert.Equal(t, int64(70), result.PromptTokenDetails.UncachedTokens)
}

// TestSafeParsePromptTokenDetails_NilData tests safeParsePromptTokenDetails with nil data
func TestSafeParsePromptTokenDetails_NilData(t *testing.T) {
	result := safeParsePromptTokenDetails(nil)
	assert.Equal(t, agentrespvo.PromptTokenDetails{}, result)
}

// TestSafeParsePromptTokenDetails_EmptyMap tests safeParsePromptTokenDetails with empty map
func TestSafeParsePromptTokenDetails_EmptyMap(t *testing.T) {
	data := map[string]any{}
	result := safeParsePromptTokenDetails(data)
	assert.Equal(t, agentrespvo.PromptTokenDetails{}, result)
}

// TestSafeParsePromptTokenDetails_OnlyCachedTokens tests safeParsePromptTokenDetails with only cached tokens
func TestSafeParsePromptTokenDetails_OnlyCachedTokens(t *testing.T) {
	data := map[string]any{
		"cached_tokens": 100.0,
	}
	result := safeParsePromptTokenDetails(data)
	assert.Equal(t, int64(100), result.CachedTokens)
	assert.Equal(t, int64(0), result.UncachedTokens)
}

// TestSafeParsePromptTokenDetails_OnlyUncachedTokens tests safeParsePromptTokenDetails with only uncached tokens
func TestSafeParsePromptTokenDetails_OnlyUncachedTokens(t *testing.T) {
	data := map[string]any{
		"uncached_tokens": 200.0,
	}
	result := safeParsePromptTokenDetails(data)
	assert.Equal(t, int64(0), result.CachedTokens)
	assert.Equal(t, int64(200), result.UncachedTokens)
}

// TestFormatTimeToISO8601_ZeroTimestamp tests formatTimeToISO8601 with zero timestamp
func TestFormatTimeToISO8601_ZeroTimestamp(t *testing.T) {
	result := formatTimeToISO8601(0)
	assert.Equal(t, "", result)
}

// TestFormatTimeToISO8601_ValidTimestamp tests formatTimeToISO8601 with valid timestamp
func TestFormatTimeToISO8601_ValidTimestamp(t *testing.T) {
	result := formatTimeToISO8601(1609459200000)
	assert.NotEmpty(t, result)
	assert.Contains(t, result, "T")
	// Note: The timezone may be local, not UTC, so we don't check for "Z"
}

// TestFormatTimeToISO8601_TimestampWithMilliseconds tests formatTimeToISO8601 with milliseconds
func TestFormatTimeToISO8601_TimestampWithMilliseconds(t *testing.T) {
	result := formatTimeToISO8601(1609459200123)
	assert.NotEmpty(t, result)
	// Note: The actual format depends on local timezone, so we just check it's not empty
}

// TestFormatTimeToISO8601_NegativeTimestamp tests formatTimeToISO8601 with negative timestamp
func TestFormatTimeToISO8601_NegativeTimestamp(t *testing.T) {
	result := formatTimeToISO8601(-1000)
	assert.NotEmpty(t, result)
}
