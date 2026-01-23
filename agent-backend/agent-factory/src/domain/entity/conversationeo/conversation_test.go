package conversationeo

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
)

func TestConversation(t *testing.T) {
	conversation := &Conversation{
		ConversationPO: &dapo.ConversationPO{
			ID:   "conv-123",
			Topic: "Test Topic",
		},
		Messages: []*dapo.ConversationMsgPO{
			{ID: "msg-1", Content: "Hello"},
			{ID: "msg-2", Content: "World"},
		},
	}

	if conversation.ID != "conv-123" {
		t.Errorf("ID = %q, want %q", conversation.ID, "conv-123")
	}
	if conversation.Topic != "Test Topic" {
		t.Errorf("Topic = %q, want %q", conversation.Topic, "Test Topic")
	}
	if len(conversation.Messages) != 2 {
		t.Errorf("Messages length = %d, want 2", len(conversation.Messages))
	}
}

func TestConversation_Empty(t *testing.T) {
	conversation := &Conversation{}

	if conversation.ConversationPO != nil {
		t.Error("ConversationPO should be nil")
	}
	if conversation.Messages != nil {
		t.Error("Messages should be nil")
	}
}

func TestConversation_NilPO(t *testing.T) {
	conversation := &Conversation{
		Messages: []*dapo.ConversationMsgPO{},
	}

	if conversation.ConversationPO != nil {
		t.Error("ConversationPO should be nil")
	}
	if len(conversation.Messages) != 0 {
		t.Error("Messages should be empty")
	}
}

func TestConversation_NilMessages(t *testing.T) {
	conversation := &Conversation{
		ConversationPO: &dapo.ConversationPO{},
		Messages:       nil,
	}

	if conversation.Messages != nil {
		t.Error("Messages should be nil")
	}
}
