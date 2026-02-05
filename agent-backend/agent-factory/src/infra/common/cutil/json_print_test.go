package cutil

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestPrintFormatJSONString(t *testing.T) {
	tests := []struct {
		name    string
		jsonStr string
		prefix  string
	}{
		{
			name:    "valid JSON string",
			jsonStr: `{"name":"John","age":30}`,
			prefix:  "Test",
		},
		{
			name:    "nested JSON",
			jsonStr: `{"person":{"name":"John"}}`,
			prefix:  "Data",
		},
		{
			name:    "empty object",
			jsonStr: `{}`,
			prefix:  "Empty",
		},
		{
			name:    "empty string",
			jsonStr: "",
			prefix:  "EmptyStr",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := PrintFormatJSONString(tt.jsonStr, tt.prefix)

			if tt.jsonStr == "" {
				assert.NoError(t, err, "PrintFormatJSONString should not return error for empty string")
			} else {
				assert.NoError(t, err, "PrintFormatJSONString should not return error")
			}
		})
	}
}

func TestPrintFormatJSON(t *testing.T) {
	tests := []struct {
		name   string
		input  interface{}
		prefix string
	}{
		{
			name:   "simple map",
			input:  map[string]interface{}{"name": "John", "age": 30},
			prefix: "Data",
		},
		{
			name:   "nested map",
			input:  map[string]interface{}{"person": map[string]interface{}{"name": "John"}},
			prefix: "Nested",
		},
		{
			name:   "slice",
			input:  []interface{}{"a", "b", "c"},
			prefix: "Slice",
		},
		{
			name:   "string",
			input:  "test",
			prefix: "String",
		},
		{
			name:   "nil",
			input:  nil,
			prefix: "Nil",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := PrintFormatJSON(tt.input, tt.prefix)
			assert.NoError(t, err, "PrintFormatJSON should not return error")
		})
	}
}
