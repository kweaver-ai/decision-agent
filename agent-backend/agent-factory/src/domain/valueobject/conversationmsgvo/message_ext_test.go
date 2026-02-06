package conversationmsgvo

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/agentresperr"
	"github.com/stretchr/testify/assert"
)

func TestMessageExt_IsInterrupted(t *testing.T) {
	tests := []struct {
		name     string
		ext      *MessageExt
		expected bool
	}{
		{
			name:     "nil interrupt info",
			ext:      &MessageExt{},
			expected: false,
		},
		{
			name:     "nil ext",
			ext:      nil,
			expected: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.ext != nil {
				assert.Equal(t, tt.expected, tt.ext.IsInterrupted())
			}
		})
	}
}

func TestMessageExt_Fields(t *testing.T) {
	ext := &MessageExt{
		RelatedQueries: []string{"What is AI?", "How does ML work?"},
		TotalTime:      2.5,
		TotalTokens:    1000,
		TTFT:           500,
		AgentRunID:     "run-123",
	}

	assert.NotNil(t, ext)
	assert.Len(t, ext.RelatedQueries, 2)
	assert.Equal(t, "What is AI?", ext.RelatedQueries[0])
	assert.Equal(t, 2.5, ext.TotalTime)
	assert.Equal(t, int64(1000), ext.TotalTokens)
	assert.Equal(t, int64(500), ext.TTFT)
	assert.Equal(t, "run-123", ext.AgentRunID)
	assert.Nil(t, ext.InterruptInfo)
	assert.Nil(t, ext.Error)
}

func TestMessageExt_WithError(t *testing.T) {
	err := agentresperr.NewRespError(agentresperr.RespErrorTypeAgentFactory, "test error")

	ext := &MessageExt{
		Error: err,
	}

	assert.NotNil(t, ext.Error)
	assert.Equal(t, agentresperr.RespErrorTypeAgentFactory, ext.Error.Type)
	assert.Equal(t, "test error", ext.Error.Error)
}

func TestMessageExt_Empty(t *testing.T) {
	ext := &MessageExt{}

	assert.Nil(t, ext.InterruptInfo)
	assert.Nil(t, ext.RelatedQueries)
	assert.Equal(t, 0.0, ext.TotalTime)
	assert.Equal(t, int64(0), ext.TotalTokens)
	assert.Equal(t, int64(0), ext.TTFT)
	assert.Empty(t, ext.AgentRunID)
	assert.Nil(t, ext.Error)
}
