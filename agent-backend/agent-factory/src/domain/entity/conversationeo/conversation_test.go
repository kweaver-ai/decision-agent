package conversationeo

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
)

func TestConversation_NewConversation(t *testing.T) {
	conv := &Conversation{
		ConversationPO: &dapo.ConversationPO{
			ID:    "conv-123",
			Title: "Test Conversation",
		},
		Messages: []*dapo.ConversationMsgPO{},
	}

	assert.NotNil(t, conv)
	assert.NotNil(t, conv.ConversationPO)
	assert.NotNil(t, conv.Messages)
	assert.Equal(t, "conv-123", conv.ID)
	assert.Equal(t, "Test Conversation", conv.Title)
}

func TestConversation_WithMessages(t *testing.T) {
	content1 := "Hello"
	content2 := "World"
	messages := []*dapo.ConversationMsgPO{
		{ID: "msg-1", Content: &content1},
		{ID: "msg-2", Content: &content2},
	}

	conv := &Conversation{
		ConversationPO: &dapo.ConversationPO{
			ID:    "conv-456",
			Title: "Test",
		},
		Messages: messages,
	}

	assert.Equal(t, 2, len(conv.Messages))
	assert.Equal(t, "msg-1", conv.Messages[0].ID)
	assert.Equal(t, "msg-2", conv.Messages[1].ID)
}

func TestConversation_NilConversationPO(t *testing.T) {
	conv := &Conversation{
		ConversationPO: nil,
		Messages:        []*dapo.ConversationMsgPO{},
	}

	assert.Nil(t, conv.ConversationPO)
	assert.NotNil(t, conv.Messages)
}

func TestConversation_NilMessages(t *testing.T) {
	conv := &Conversation{
		ConversationPO: &dapo.ConversationPO{
			ID:    "conv-789",
			Title: "Test",
		},
		Messages: nil,
	}

	assert.NotNil(t, conv.ConversationPO)
	assert.Nil(t, conv.Messages)
}
