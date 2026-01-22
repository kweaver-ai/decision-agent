package cutil

import (
	"encoding/json"
	"testing"
)

// TestMergeJSONStrings tests the MergeJSONStrings function with various cases.
func TestMergeJSONStrings(t *testing.T) {
	tests := []struct {
		name       string
		jsonStr1   string
		jsonStr2   string
		expected   string
		shouldFail bool
	}{
		{
			name: "Basic Merge",
			jsonStr1: `{
                "name": "John",
                "age": 30,
                "hobbies": ["reading"]
            }`,
			jsonStr2: `{
                "age": 31,
                "hobbies": ["cycling"],
                "location": "New York"
            }`,
			expected: `{
                "hobbies": ["cycling"],
                "location": "New York",
                "name": "John",
                "age": 31
            }`,
			shouldFail: false,
		},
		{
			name: "Nested Merge",
			jsonStr1: `{
                "person": {
                    "name": "John",
                    "age": 30
                },
                "hobbies": ["reading"]
            }`,
			jsonStr2: `{
                "person": {
                    "age": 31
                },
                "hobbies": ["cycling"],
                "location": "New York"
            }`,
			expected: `{
                "hobbies": ["cycling"],
                "location": "New York",
                "person": {
                    "age": 31,
                    "name": "John"
                }
            }`,
			shouldFail: false,
		},
		{
			name:       "Malformed JSON",
			jsonStr1:   `{"name": "John", "age": 30`,
			jsonStr2:   `{"age": 31}`,
			expected:   "",
			shouldFail: true,
		},

		{
			name: "Null Values",
			jsonStr1: `{
                "person": null,
                "hobbies": ["reading"]
            }`,
			jsonStr2: `{
                "person": {
                    "age": 31
                },
                "hobbies": ["cycling"],
                "location": "New York"
            }`,
			expected: `{
                "hobbies": ["cycling"],
                "location": "New York",
                "person": {
                    "age": 31   
                }
            }`,
			shouldFail: false,
		},
		{
			name: "Null Values with additional keys",
			jsonStr1: `{
                "person": {
                    "age": 31
                },
                "person2": {
                    "age": 31
                },
                "hobbies": ["reading"]
            }`,
			jsonStr2: `{
                "person": null,
                "hobbies": ["cycling"],
                "location": "New York"
            }`,
			expected: `{
                "hobbies": ["cycling"],
                "location": "New York", 
                "person": null,
                "person2": {
                    "age": 31   
                }
            }`,
			shouldFail: false,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			var result string

			var err error
			result, err = MergeJSONStrings(test.jsonStr1, test.jsonStr2)

			if test.shouldFail {
				if err == nil {
					t.Errorf("expected failure but got success")
				}

				return
			}

			if err != nil {
				t.Errorf("unexpected error: %v", err)
			}

			b, err := JSONStrCompare(result, test.expected)
			if err != nil {
				t.Errorf("unexpected error: %v", err)
			}

			if !b {
				t.Errorf("expected %v, got %v", test.expected, result)
			}
		})
	}
}

type UserDetail struct {
	Name     string `json:"name"`
	Age      int    `json:"age"`
	Location string `json:"location"`
}

type User struct {
	Hobbies []string   `json:"hobbies"`
	Details UserDetail `json:"details"`
}

// TestMergeMapInterface tests the MergeMapInterface function with various cases.
func TestMergeMapInterface(t *testing.T) {
	tests := []struct {
		name       string
		map1       map[string]interface{}
		interface2 interface{}
		expected   map[string]interface{}
		shouldFail bool
	}{
		{
			name: "Basic Merge with map",
			map1: map[string]interface{}{
				"name": "Alice",
				"age":  28,
			},
			interface2: map[string]interface{}{
				"age":      29,
				"location": "London",
			},
			expected: map[string]interface{}{
				"name":     "Alice",
				"age":      29,
				"location": "London",
			},
			shouldFail: false,
		},
		{
			name: "Nested Merge with map",
			map1: map[string]interface{}{
				"person": map[string]interface{}{
					"name": "Alice",
					"age":  28,
				},
			},
			interface2: map[string]interface{}{
				"person": map[string]interface{}{
					"age": 29,
				},
			},
			expected: map[string]interface{}{
				"person": map[string]interface{}{
					"name": "Alice",
					"age":  29,
				},
			},
			shouldFail: false,
		},
		{
			name: "Merge with incompatible types",
			map1: map[string]interface{}{
				"age": "twenty-eight",
			},
			interface2: map[string]interface{}{
				"age": 28,
			},
			expected: map[string]interface{}{
				"age": 28,
			},
			shouldFail: false,
		},
		{
			name: "Deeply Nested Structs",
			map1: map[string]interface{}{
				"user": map[string]interface{}{
					"details": map[string]interface{}{
						"name": "Bob",
						"age":  40,
					},
				},
			},
			interface2: map[string]interface{}{
				"user": User{
					Hobbies: []string{"reading", "cycling"},
					Details: UserDetail{
						Age:      41,
						Location: "Paris",
					},
				},
			},
			expected: map[string]interface{}{
				"user": map[string]interface{}{
					"hobbies": []string{"reading", "cycling"},
					"details": map[string]interface{}{
						"name":     "",
						"age":      41,
						"location": "Paris",
					},
				},
			},
			shouldFail: false,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			err := MergeMapInterface(test.map1, test.interface2)

			if test.shouldFail {
				if err == nil {
					t.Errorf("expected failure but got success")
				}

				return
			}

			if err != nil {
				t.Errorf("unexpected error: %v", err)
			}

			// Convert maps to JSON strings for comparison
			expectedJSON, err := json.Marshal(test.expected)
			if err != nil {
				t.Errorf("failed to marshal expected map: %v", err)
			}

			resultJSON, err := json.Marshal(test.map1)
			if err != nil {
				t.Errorf("failed to marshal result map: %v", err)
			}

			if string(expectedJSON) != string(resultJSON) {
				t.Errorf("expected %v, got %v", string(expectedJSON), string(resultJSON))
			}
		})
	}
}
