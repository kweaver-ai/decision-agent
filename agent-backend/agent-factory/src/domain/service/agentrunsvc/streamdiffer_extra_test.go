package agentsvc

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

// TestFormatSSEMessage_Basic tests formatSSEMessage with basic data
func TestFormatSSEMessage_Basic(t *testing.T) {
	data := "test message"
	result := formatSSEMessage(data)
	expected := "data: test message\n\n"
	assert.Equal(t, expected, string(result))
}

// TestFormatSSEMessage_EmptyString tests formatSSEMessage with empty string
func TestFormatSSEMessage_EmptyString(t *testing.T) {
	data := ""
	result := formatSSEMessage(data)
	expected := "data: \n\n"
	assert.Equal(t, expected, string(result))
}

// TestFormatSSEMessage_WithNewlines tests formatSSEMessage with data containing newlines
func TestFormatSSEMessage_WithNewlines(t *testing.T) {
	data := "line1\nline2"
	result := formatSSEMessage(data)
	expected := "data: line1\nline2\n\n"
	assert.Equal(t, expected, string(result))
}

// TestFormatSSEMessage_WithJSON tests formatSSEMessage with JSON data
func TestFormatSSEMessage_WithJSON(t *testing.T) {
	data := `{"key":"value"}`
	result := formatSSEMessage(data)
	expected := "data: {\"key\":\"value\"}\n\n"
	assert.Equal(t, expected, string(result))
}

// TestFormatChange_Basic tests formatChange with basic change
func TestFormatChange_Basic(t *testing.T) {
	ch := Change{
		SeqID:   1,
		Key:     []interface{}{"root", "field"},
		Content: "value",
		Action:  "upsert",
	}

	result := formatChange(ch)
	assert.Contains(t, result, `"seq_id": 1`)
	assert.Contains(t, result, `"action": "upsert"`)
	assert.Contains(t, result, `"key":`)
	assert.Contains(t, result, `"content":`)
}

// TestFormatChange_EmptyKey tests formatChange with empty key path
func TestFormatChange_EmptyKey(t *testing.T) {
	ch := Change{
		SeqID:   0,
		Key:     []interface{}{},
		Content: nil,
		Action:  "remove",
	}

	result := formatChange(ch)
	assert.Contains(t, result, `"seq_id": 0`)
	assert.Contains(t, result, `"action": "remove"`)
	assert.Contains(t, result, `"key": []`)
	assert.Contains(t, result, `"content": null`)
}

// TestFormatChange_NumericKey tests formatChange with numeric key
func TestFormatChange_NumericKey(t *testing.T) {
	ch := Change{
		SeqID:   5,
		Key:     []interface{}{"array", 0, "field"},
		Content: 123,
		Action:  "append",
	}

	result := formatChange(ch)
	assert.Contains(t, result, `"seq_id": 5`)
	assert.Contains(t, result, `"action": "append"`)
}

// TestFormatChange_StringContent tests formatChange with string content
func TestFormatChange_StringContent(t *testing.T) {
	ch := Change{
		SeqID:   2,
		Key:     []interface{}{"text"},
		Content: "hello world",
		Action:  "upsert",
	}

	result := formatChange(ch)
	assert.Contains(t, result, `"content": "hello world"`)
}

// TestFormatChange_ObjectContent tests formatChange with object content
func TestFormatChange_ObjectContent(t *testing.T) {
	ch := Change{
		SeqID:   3,
		Key:     []interface{}{"obj"},
		Content: map[string]interface{}{"nested": "value"},
		Action:  "upsert",
	}

	result := formatChange(ch)
	assert.Contains(t, result, `"content":`)
}
