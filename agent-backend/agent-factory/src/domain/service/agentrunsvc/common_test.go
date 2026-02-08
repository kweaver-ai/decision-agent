package agentsvc

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/constant"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/agentrespvo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/agentrespvo/daresvo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/daconfvalobj"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/daconfvalobj/skillvalobj"
	agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
	"github.com/stretchr/testify/assert"
)

func TestAgentConfig2AgentCallConfig(t *testing.T) {
	ctx := context.Background()
	req := &agentreq.ChatReq{
		AgentID:        "agent-123",
		ConversationID: "conv-456",
		AgentRunID:     "run-789",
	}

	agentConfig := &daconfvalobj.Config{
		SystemPrompt: "You are a helpful assistant",
		Skill: &skillvalobj.Skill{
			Tools: []*skillvalobj.SkillTool{{ToolID: "tool1", ToolBoxID: "box1"}},
		},
	}

	result := AgentConfig2AgentCallConfig(ctx, agentConfig, req)

	assert.Equal(t, "agent-123", result.AgentID)
	assert.Equal(t, "conv-456", result.ConversationID)
	assert.Equal(t, "run-789", result.SessionID)
	assert.Equal(t, "You are a helpful assistant", result.Config.SystemPrompt)
	assert.NotNil(t, result.Skill)
	assert.Len(t, result.Skill.Tools, 1)
}

func TestAgentConfig2AgentCallConfigWithNilSkill(t *testing.T) {
	ctx := context.Background()
	req := &agentreq.ChatReq{
		AgentID:        "agent-123",
		ConversationID: "conv-456",
		AgentRunID:     "run-789",
	}

	agentConfig := &daconfvalobj.Config{
		SystemPrompt: "You are a helpful assistant",
		Skill:         nil,
	}

	result := AgentConfig2AgentCallConfig(ctx, agentConfig, req)

	assert.NotNil(t, result.Skill)
	assert.Len(t, result.Skill.Tools, 0)
	assert.Len(t, result.Skill.Agents, 0)
	assert.Len(t, result.Skill.MCPs, 0)
}

func TestAgentConfig2AgentCallConfigDebug(t *testing.T) {
	ctx := context.Background()
	req := &agentreq.DebugReq{
		AgentID:    "agent-123",
		AgentRunID: "run-789",
	}

	agentConfig := &daconfvalobj.Config{
		SystemPrompt: "You are a helpful assistant",
	}

	result := AgentConfig2AgentCallConfigDebug(ctx, agentConfig, req)

	assert.Equal(t, "agent-123", result.AgentID)
	assert.Equal(t, "run-789", result.SessionID)
	assert.NotNil(t, result.Skill)
}

func TestCalculateTTFT(t *testing.T) {
	tests := []struct {
		name        string
		startTime   int64
		progresses  []*agentrespvo.Progress
		callType    constant.CallType
		wantGreater bool
	}{
		{
			name:        "empty progress returns 0",
			startTime:   1000,
			progresses:  []*agentrespvo.Progress{},
			callType:    constant.Chat,
			wantGreater: false,
		},
		{
			name:      "nil progress returns 0",
			startTime: 1000,
			progresses: []*agentrespvo.Progress{
				{Stage: "llm"},
			},
			callType:    constant.DebugChat,
			wantGreater: true,
		},
		{
			name:      "unknown call type returns 0",
			startTime: 1000,
			progresses: []*agentrespvo.Progress{
				{Stage: "llm"},
			},
			callType:    "unknown",
			wantGreater: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := CalculateTTFT(tt.startTime, tt.progresses, tt.callType)

			if tt.wantGreater {
				assert.Greater(t, result, int64(0))
			} else {
				assert.Equal(t, int64(0), result)
			}
		})
	}
}

func TestGenerateAssistantMsg(t *testing.T) {
	ctx := context.Background()
	req := &agentreq.ChatReq{
		AgentID: "agent-123",
	}
	result := &daresvo.DataAgentRes{}

	msg, err := GenerateAssistantMsg(ctx, req, result)

	assert.NoError(t, err)
	assert.NotNil(t, msg)
}
