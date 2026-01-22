package cutil

import "testing"

// TestJSONStrCompare tests the JSONStrCompare function.
func TestJSONStrCompare(t *testing.T) {
	tests := []struct {
		name     string
		jsonStr1 string
		jsonStr2 string
		expected bool
	}{
		{
			name:     "Equal JSON",
			jsonStr1: `{"name": "John", "age": 30}`,
			jsonStr2: `{"age": 30, "name": "John"}`,
			expected: true,
		},
		{
			name:     "Non-equal JSON",
			jsonStr1: `{"name": "John", "age": 30}`,
			jsonStr2: `{"name": "Doe", "age": 30}`,
			expected: false,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			result, err := JSONStrCompare(test.jsonStr1, test.jsonStr2)
			if err != nil {
				t.Errorf("unexpected error: %v", err)
			}

			if result != test.expected {
				t.Errorf("expected %v, got %v", test.expected, result)
			}
		})
	}
}
