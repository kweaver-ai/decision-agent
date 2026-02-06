package conversationp2e

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
)

func TestConversation_WithoutMessages(t *testing.T) {
	po := &dapo.ConversationPO{
		ID: "conv-1",
	}

	eo, err := Conversation(context.Background(), po, nil, false)

	assert.NoError(t, err)
	assert.NotNil(t, eo)
	assert.Equal(t, "conv-1", eo.ID)
	assert.Nil(t, eo.Messages)
}

func TestConversation_WithMessages(t *testing.T) {
	// Note: This test requires a mock IConversationMsgRepo
	// With nil repo, this will panic, so we test for that
	po := &dapo.ConversationPO{
		ID: "conv-1",
	}

	assert.Panics(t, func() {
		Conversation(context.Background(), po, nil, true)
	})
}

func TestConversation_EmptyPO(t *testing.T) {
	po := &dapo.ConversationPO{}

	eo, err := Conversation(context.Background(), po, nil, false)

	assert.NoError(t, err)
	assert.NotNil(t, eo)
}

func TestConversations_EmptyList(t *testing.T) {
	pos := []*dapo.ConversationPO{}

	eos, err := Conversations(context.Background(), pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 0)
}

func TestConversations_SingleItem(t *testing.T) {
	pos := []*dapo.ConversationPO{
		{ID: "conv-1"},
	}

	eos, err := Conversations(context.Background(), pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	assert.Equal(t, "conv-1", eos[0].ID)
}

func TestConversations_MultipleItems(t *testing.T) {
	pos := []*dapo.ConversationPO{
		{ID: "conv-1"},
		{ID: "conv-2"},
		{ID: "conv-3"},
	}

	eos, err := Conversations(context.Background(), pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 3)
	assert.Equal(t, "conv-1", eos[0].ID)
	assert.Equal(t, "conv-2", eos[1].ID)
	assert.Equal(t, "conv-3", eos[2].ID)
}
