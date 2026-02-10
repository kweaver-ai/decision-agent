package conversationmsgreq

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestListReq_StructFields(t *testing.T) {
	req := &ListReq{
		ConversationID: "conv-123",
	}

	assert.Equal(t, "conv-123", req.ConversationID)
}

func TestListReq_Empty(t *testing.T) {
	req := &ListReq{}

	assert.Empty(t, req.ConversationID)
}

func TestListReq_WithConversationID(t *testing.T) {
	ids := []string{
		"conv-001",
		"test-conversation",
		"CONV-ABC-123",
		"",
	}

	for _, id := range ids {
		req := &ListReq{ConversationID: id}
		assert.Equal(t, id, req.ConversationID)
	}
}
