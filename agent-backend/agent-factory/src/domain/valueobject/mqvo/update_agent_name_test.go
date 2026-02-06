package mqvo

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/stretchr/testify/assert"
)

func TestNewUpdateAgentNameMqMsg(t *testing.T) {
	msg := NewUpdateAgentNameMqMsg("agent-123", "Test Agent")

	assert.NotNil(t, msg)
	assert.Equal(t, "agent-123", msg.ID)
	assert.Equal(t, "Test Agent", msg.Name)
	assert.Equal(t, cdaenum.ResourceTypeDataAgent, msg.Type)
}

func TestUpdateAgentNameMqMsg_Fields(t *testing.T) {
	msg := &UpdateAgentNameMqMsg{
		ID:   "test-id",
		Type: cdaenum.ResourceTypeDataAgentTpl,
		Name: "Test Name",
	}

	assert.Equal(t, "test-id", msg.ID)
	assert.Equal(t, cdaenum.ResourceTypeDataAgentTpl, msg.Type)
	assert.Equal(t, "Test Name", msg.Name)
}

func TestUpdateAgentNameMqMsg_Empty(t *testing.T) {
	msg := &UpdateAgentNameMqMsg{}

	assert.Empty(t, msg.ID)
	assert.Empty(t, msg.Name)
	assert.Equal(t, cdaenum.ResourceType(""), msg.Type)
}
