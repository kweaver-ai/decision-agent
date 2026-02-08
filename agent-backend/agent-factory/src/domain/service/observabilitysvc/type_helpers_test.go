package observabilitysvc

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/agentrespvo"
	"github.com/stretchr/testify/assert"
)

func TestSafeGetString(t *testing.T) {
	tests := []struct {
		name     string
		m        map[string]any
		key      string
		expected string
	}{
		{
			name:     "existing string value",
			m:        map[string]any{"key": "value"},
			key:      "key",
			expected: "value",
		},
		{
			name:     "non-existent key",
			m:        map[string]any{"other": "value"},
			key:      "key",
			expected: "",
		},
		{
			name:     "nil value",
			m:        map[string]any{"key": nil},
			key:      "key",
			expected: "",
		},
		{
			name:     "non-string value",
			m:        map[string]any{"key": 123},
			key:      "key",
			expected: "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := safeGetString(tt.m, tt.key)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestSafeGetBool(t *testing.T) {
	tests := []struct {
		name     string
		m        map[string]any
		key      string
		expected bool
	}{
		{
			name:     "true value",
			m:        map[string]any{"key": true},
			key:      "key",
			expected: true,
		},
		{
			name:     "false value",
			m:        map[string]any{"key": false},
			key:      "key",
			expected: false,
		},
		{
			name:     "non-existent key",
			m:        map[string]any{"other": true},
			key:      "key",
			expected: false,
		},
		{
			name:     "nil value",
			m:        map[string]any{"key": nil},
			key:      "key",
			expected: false,
		},
		{
			name:     "non-bool value",
			m:        map[string]any{"key": "true"},
			key:      "key",
			expected: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := safeGetBool(tt.m, tt.key)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestSafeGetFloat64(t *testing.T) {
	tests := []struct {
		name     string
		m        map[string]any
		key      string
		expected float64
	}{
		{
			name:     "existing float value",
			m:        map[string]any{"key": 123.45},
			key:      "key",
			expected: 123.45,
		},
		{
			name:     "zero value",
			m:        map[string]any{"key": 0.0},
			key:      "key",
			expected: 0.0,
		},
		{
			name:     "non-existent key",
			m:        map[string]any{"other": 123.45},
			key:      "key",
			expected: 0.0,
		},
		{
			name:     "nil value",
			m:        map[string]any{"key": nil},
			key:      "key",
			expected: 0.0,
		},
		{
			name:     "non-float value",
			m:        map[string]any{"key": "123.45"},
			key:      "key",
			expected: 0.0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := safeGetFloat64(tt.m, tt.key)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestSafeGetInt64(t *testing.T) {
	tests := []struct {
		name     string
		m        map[string]any
		key      string
		expected int64
	}{
		{
			name:     "existing float value that fits in int64",
			m:        map[string]any{"key": 123.0},
			key:      "key",
			expected: 123,
		},
		{
			name:     "zero value",
			m:        map[string]any{"key": 0.0},
			key:      "key",
			expected: 0,
		},
		{
			name:     "non-existent key",
			m:        map[string]any{"other": 123.0},
			key:      "key",
			expected: 0,
		},
		{
			name:     "nil value",
			m:        map[string]any{"key": nil},
			key:      "key",
			expected: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := safeGetInt64(tt.m, tt.key)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestSafeParseSkillInfo(t *testing.T) {
	tests := []struct {
		name     string
		data     any
		expected *agentrespvo.SkillInfo
	}{
		{
			name: "valid skill info",
			data: map[string]any{
				"type":    "tool",
				"name":    "search",
				"checked": true,
				"args": []any{
					map[string]any{
						"name":  "query",
						"value": "test",
						"type":  "string",
					},
				},
			},
			expected: &agentrespvo.SkillInfo{
				Type:    "tool",
				Name:    "search",
				Checked: true,
				Args: []agentrespvo.Arg{
					{
						Name:  "query",
						Value: "test",
						Type:  "string",
					},
				},
			},
		},
		{
			name:     "nil data",
			data:     nil,
			expected: nil,
		},
		{
			name:     "invalid data type",
			data:     "string",
			expected: nil,
		},
		{
			name:     "empty map",
			data:     map[string]any{},
			expected: &agentrespvo.SkillInfo{},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := safeParseSkillInfo(tt.data)
			if tt.expected == nil {
				assert.Nil(t, result)
			} else {
				assert.NotNil(t, result)
				assert.Equal(t, tt.expected.Type, result.Type)
				assert.Equal(t, tt.expected.Name, result.Name)
				assert.Equal(t, tt.expected.Checked, result.Checked)
			}
		})
	}
}

func TestSafeParseTokenUsage(t *testing.T) {
	tests := []struct {
		name     string
		data     any
		expected agentrespvo.TokenUsage
	}{
		{
			name: "valid token usage",
			data: map[string]any{
				"prompt_tokens":     100.0,
				"completion_tokens": 50.0,
				"total_tokens":      150.0,
			},
			expected: agentrespvo.TokenUsage{
				PromptTokens:     100,
				CompletionTokens: 50,
				TotalTokens:      150,
			},
		},
		{
			name:     "nil data",
			data:     nil,
			expected: agentrespvo.TokenUsage{},
		},
		{
			name:     "invalid data type",
			data:     "string",
			expected: agentrespvo.TokenUsage{},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := safeParseTokenUsage(tt.data)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestFormatTimeToISO8601(t *testing.T) {
	tests := []struct {
		name      string
		timestamp int64
		wantEmpty bool
	}{
		{
			name:      "zero timestamp",
			timestamp: 0,
			wantEmpty: true,
		},
		{
			name:      "valid timestamp",
			timestamp: 1609459200000, // 2021-01-01 00:00:00 UTC in milliseconds
			wantEmpty: false,
		},
		{
			name:      "negative timestamp",
			timestamp: -1000,
			wantEmpty: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := formatTimeToISO8601(tt.timestamp)
			if tt.wantEmpty {
				assert.Empty(t, result)
			} else {
				assert.NotEmpty(t, result)
				assert.Contains(t, result, "T")
			}
		})
	}
}
