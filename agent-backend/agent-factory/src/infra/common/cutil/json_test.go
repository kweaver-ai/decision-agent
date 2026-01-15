package cutil

import (
	"bytes"
	"testing"

	jsoniter "github.com/json-iterator/go"
)

// TestJSON verifies that the JSON function returns a non-nil jsoniter.API instance.
func TestJSON(t *testing.T) {
	api := JSON()
	if api == nil {
		t.Error("Expected non-nil jsoniter.API, but got nil")
	}

	// Additional test to check if the returned API matches the expected config
	if api != jsoniter.ConfigCompatibleWithStandardLibrary {
		t.Error("Expected jsoniter.ConfigCompatibleWithStandardLibrary, but got different API")
	}
}

// TestJSONObjectToArray tests the JSONObjectToArray function with various cases.
func TestJSONObjectToArray(t *testing.T) {
	tests := []struct {
		input    []byte
		expected []byte
	}{
		{[]byte(`{"key1":"value1"}`), []byte(`[{"key1":"value1"}]`)},
		{[]byte(``), []byte(`[]`)}, // Test with empty JSON object
		{[]byte(`{"key2":true}`), []byte(`[{"key2":true}]`)},
		{[]byte(`{"key3":123}`), []byte(`[{"key3":123}]`)},
		// Add more cases as needed for thorough testing
	}

	for _, test := range tests {
		result := JSONObjectToArray(test.input)
		if !bytes.Equal(result, test.expected) {
			t.Errorf("Expected %s, but got %s", test.expected, result)
		}
	}
}

// TestFormatJSONString tests the FormatJSONString function to ensure it formats JSON correctly.
func TestFormatJSONString(t *testing.T) {
	tests := []struct {
		input    string
		expected string
	}{
		{
			input:    `{"key1":"value1","key2":2}`,
			expected: "{\n  \"key1\": \"value1\",\n  \"key2\": 2\n}",
		},
		{
			input:    `{"nested":{"key":true}}`,
			expected: "{\n  \"nested\": {\n    \"key\": true\n  }\n}",
		},
		{
			input:    `[{"key1":1,"key2":2,"key3":3}]`,
			expected: "[\n  {\n    \"key1\": 1,\n    \"key2\": 2,\n    \"key3\": 3\n  }\n]",
		},
		// Add more test cases if needed
	}

	for _, test := range tests {
		result, err := FormatJSONString(test.input)
		if err != nil {
			t.Errorf("Unexpected error: %v", err)
		}

		if result != test.expected {
			t.Errorf("Expected:\n%s\n but got:\n%s", test.expected, result)
		}
	}
}

// TestFormatJSON tests the FormatJSON function with various types of inputs.
func TestFormatJSON(t *testing.T) {
	tests := []struct {
		input    interface{}
		expected string
	}{
		{
			input: map[string]interface{}{
				"key1": "value1",
				"key2": 2,
			},
			expected: "{\n  \"key1\": \"value1\",\n  \"key2\": 2\n}",
		},
		{
			input: struct {
				Name  string
				Age   int
				Admin bool
			}{
				Name:  "Alice",
				Age:   30,
				Admin: true,
			},
			expected: "{\n  \"Name\": \"Alice\",\n  \"Age\": 30,\n  \"Admin\": true\n}",
		},
		// Add more test cases as needed
	}

	for _, test := range tests {
		result, err := FormatJSON(test.input)
		if err != nil {
			t.Errorf("Unexpected error: %v", err)
		}

		if result != test.expected {
			t.Errorf("Expected:\n%s\n but got:\n%s", test.expected, result)
		}
	}
}
