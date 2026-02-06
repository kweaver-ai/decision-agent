package daresvo

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/agentconfigvo"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestRelatedQuestion_Fields(t *testing.T) {
	q := &RelatedQuestion{
		Query: "What is the weather today?",
	}

	assert.Equal(t, "What is the weather today?", q.Query)
}

func TestDataAgentRes_RelatedQueries_NoQuestions(t *testing.T) {
	ctx := context.Background()
	data := []byte(`{
		"answer": {
			"final_answer": "Test answer"
		}
	}`)

	outputVars := &agentconfigvo.OutputVariablesS{
		AnswerVar: "answer",
	}

	res, err := NewDataAgentRes(ctx, data, outputVars)
	require.NoError(t, err)

	questions := res.RelatedQueries()
	// Returns an empty slice, not nil
	assert.Empty(t, questions)
}

func TestDataAgentRes_RelatedQueries_WithQuestions(t *testing.T) {
	ctx := context.Background()
	data := []byte(`{
		"answer": {
			"final_answer": "Test answer",
			"related_questions": ["Question 1?", "Question 2?", "Question 3?"]
		}
	}`)

	outputVars := &agentconfigvo.OutputVariablesS{
		AnswerVar: "answer",
	}

	res, err := NewDataAgentRes(ctx, data, outputVars)
	require.NoError(t, err)

	questions := res.RelatedQueries()
	assert.Len(t, questions, 3)
	assert.Equal(t, "Question 1?", questions[0].Query)
	assert.Equal(t, "Question 2?", questions[1].Query)
	assert.Equal(t, "Question 3?", questions[2].Query)
}
