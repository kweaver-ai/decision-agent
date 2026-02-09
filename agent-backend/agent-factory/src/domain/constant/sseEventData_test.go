package constant

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestEventStreamEventEnd(t *testing.T) {
	assert.Equal(t, "end", EventStreamEventEnd)
}

func TestSSEFieldData(t *testing.T) {
	assert.Equal(t, "data", SSEFieldData)
}

func TestDataEventEndStr_Format(t *testing.T) {
	expected := "data: event: end"
	assert.Equal(t, expected, DataEventEndStr)
}

func TestDataEventEndStr_NotEmpty(t *testing.T) {
	assert.NotEmpty(t, DataEventEndStr)
}

func TestSSEConstants_AreConsistent(t *testing.T) {
	// DataEventEndStr should contain both SSEFieldData and EventStreamEventEnd
	assert.Contains(t, DataEventEndStr, SSEFieldData)
	assert.Contains(t, DataEventEndStr, EventStreamEventEnd)
}
