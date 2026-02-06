package daresvo

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/agentconfigvo"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestDataAgentRes_GetExploreAnswerList_NotExploreType(t *testing.T) {
	ctx := context.Background()
	// Not an explore type - answer is a nested object but not an explore array
	data := []byte(`{
		"answer": {
			"answer": "Test answer content"
		}
	}`)
	outputVars := &agentconfigvo.OutputVariablesS{
		AnswerVar: "answer",
	}

	res, err := NewDataAgentRes(ctx, data, outputVars)
	require.NoError(t, err)

	answerList, ok := res.GetExploreAnswerList()
	assert.False(t, ok)
	assert.Empty(t, answerList)
}

func TestDataAgentRes_IsPromptType_NotPromptType(t *testing.T) {
	ctx := context.Background()
	// Not a prompt type - answer is a nested object but not a prompt
	data := []byte(`{
		"answer": {
			"answer": "Test answer content"
		}
	}`)
	outputVars := &agentconfigvo.OutputVariablesS{
		AnswerVar: "answer",
	}

	res, err := NewDataAgentRes(ctx, data, outputVars)
	require.NoError(t, err)

	answer, ok := res.IsPromptType()
	assert.False(t, ok)
	// Answer object is created but empty, not nil
	assert.NotNil(t, answer)
}
