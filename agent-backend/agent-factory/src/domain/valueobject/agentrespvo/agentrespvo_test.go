package agentrespvo

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewAnswerS(t *testing.T) {
	answer := NewAnswerS()
	assert.NotNil(t, answer)
	assert.NotNil(t, answer.Interventions)
	// Progress is not initialized in NewAnswerS, so we don't check it
}

func TestAnswerS_Fields(t *testing.T) {
	answer := &AnswerS{
		Interventions: Interventions{
			&Intervention{
				ToolName: "test_tool",
			},
		},
		Progress: []*Progress{
			{Stage: "llm"},
		},
	}

	assert.Len(t, answer.Interventions, 1)
	assert.Len(t, answer.Progress, 1)
	assert.Equal(t, "test_tool", answer.Interventions[0].ToolName)
	assert.Equal(t, "llm", answer.Progress[0].Stage)
}

func TestAnswerS_MarshalJSON(t *testing.T) {
	answer := &AnswerS{
		Interventions: NewInterventions(),
		Progress:      []*Progress{},
	}

	answer.SetField("test_field", "test_value")

	data, err := answer.MarshalJSON()
	assert.NoError(t, err)
	assert.NotNil(t, data)
	assert.Contains(t, string(data), "test_field")
	assert.Contains(t, string(data), "test_value")
}

func TestAnswerS_UnmarshalJSON(t *testing.T) {
	jsonData := `{
		"interventions": [],
		"_progress": [],
		"custom_field": "custom_value"
	}`

	answer := &AnswerS{}
	err := answer.UnmarshalJSON([]byte(jsonData))
	assert.NoError(t, err)
	assert.NotNil(t, answer.Interventions)
	assert.NotNil(t, answer.Progress)

	// Check that custom field was added to DynamicFields
	customValue, exists := answer.DynamicFields["custom_field"]
	assert.True(t, exists)
	assert.Equal(t, "custom_value", customValue)
}

func TestNewInterventions(t *testing.T) {
	interventions := NewInterventions()
	assert.NotNil(t, interventions)
	assert.Len(t, interventions, 0)
}

func TestInterventions_ToOutputVarMap(t *testing.T) {
	interventions := Interventions{
		&Intervention{
			ToolName: "tool1",
			ToolCallInfo: &ToolCallInfo{
				OutputVar: "var1",
			},
		},
		&Intervention{
			ToolName: "tool2",
			ToolCallInfo: &ToolCallInfo{
				OutputVar: "var1",
			},
		},
		&Intervention{
			ToolName: "tool3",
			ToolCallInfo: &ToolCallInfo{
				OutputVar: "var2",
			},
		},
		&Intervention{
			ToolName: "tool4",
			ToolCallInfo: nil,
		},
		&Intervention{
			ToolName: "tool5",
			ToolCallInfo: &ToolCallInfo{
				OutputVar: "",
			},
		},
	}

	outputVarMap := interventions.ToOutputVarMap()
	assert.Len(t, outputVarMap, 2)
	assert.Len(t, outputVarMap["var1"], 2)
	assert.Len(t, outputVarMap["var2"], 1)
}

func TestInterventions_ToOutputVarMap_Empty(t *testing.T) {
	interventions := Interventions{}
	outputVarMap := interventions.ToOutputVarMap()
	assert.NotNil(t, outputVarMap)
	assert.Len(t, outputVarMap, 0)
}

func TestIntervention_Fields(t *testing.T) {
	intervention := &Intervention{
		ToolName: "search_tool",
		ToolCallInfo: &ToolCallInfo{
			ToolName:   "search",
			Args:       map[string]string{"query": "test"},
			AssignType: "direct",
			OutputVar:  "result",
		},
	}

	assert.Equal(t, "search_tool", intervention.ToolName)
	assert.NotNil(t, intervention.ToolCallInfo)
	assert.Equal(t, "search", intervention.ToolCallInfo.ToolName)
	assert.Equal(t, "direct", intervention.ToolCallInfo.AssignType)
	assert.Equal(t, "result", intervention.ToolCallInfo.OutputVar)
}

func TestIntervention_NilToolCallInfo(t *testing.T) {
	intervention := &Intervention{
		ToolName:     "test_tool",
		ToolCallInfo: nil,
	}

	assert.Equal(t, "test_tool", intervention.ToolName)
	assert.Nil(t, intervention.ToolCallInfo)
}

func TestToolCallInfo_Fields(t *testing.T) {
	toolCallInfo := &ToolCallInfo{
		ToolName:   "search",
		Args:       []string{"arg1", "arg2"},
		AssignType: "expression",
		OutputVar:  "output",
	}

	assert.Equal(t, "search", toolCallInfo.ToolName)
	assert.NotNil(t, toolCallInfo.Args)
	assert.Equal(t, "expression", toolCallInfo.AssignType)
	assert.Equal(t, "output", toolCallInfo.OutputVar)
}

func TestProgress_Fields(t *testing.T) {
	progress := &Progress{
		ID:        "progress-1",
		AgentName: "TestAgent",
		Stage:     "llm",
		Answer:    "This is the answer",
		Think:     "This is the thinking",
		Status:    "completed",
		SkillInfo: &SkillInfo{
			Type: "tool",
			Name: "search",
		},
		InputMessage:            "input",
		Interrupted:             false,
		StartTime:               100.0,
		EndTime:                 200.0,
		EstimatedInputTokens:    100,
		EstimatedOutputTokens:   200,
		EstimatedRatioTokens:    2.0,
		TokenUsage:              TokenUsage{PromptTokens: 100, CompletionTokens: 200, TotalTokens: 300},
	}

	assert.Equal(t, "progress-1", progress.ID)
	assert.Equal(t, "TestAgent", progress.AgentName)
	assert.Equal(t, "llm", progress.Stage)
	assert.Equal(t, "This is the answer", progress.Answer)
	assert.Equal(t, "completed", progress.Status)
	assert.NotNil(t, progress.SkillInfo)
	assert.Equal(t, 100.0, progress.StartTime)
	assert.Equal(t, 200.0, progress.EndTime)
	assert.Equal(t, int64(100), progress.EstimatedInputTokens)
	assert.Equal(t, int64(200), progress.EstimatedOutputTokens)
	assert.Equal(t, 2.0, progress.EstimatedRatioTokens)
}

func TestProgress_Empty(t *testing.T) {
	progress := &Progress{}

	assert.Empty(t, progress.ID)
	assert.Empty(t, progress.AgentName)
	assert.Empty(t, progress.Stage)
	assert.Nil(t, progress.Answer)
	assert.Nil(t, progress.Think)
	assert.Empty(t, progress.Status)
	assert.Nil(t, progress.SkillInfo)
	assert.Nil(t, progress.InputMessage)
	assert.False(t, progress.Interrupted)
	assert.Equal(t, float64(0), progress.StartTime)
	assert.Equal(t, float64(0), progress.EndTime)
	assert.Equal(t, int64(0), progress.EstimatedInputTokens)
	assert.Equal(t, int64(0), progress.EstimatedOutputTokens)
	assert.Equal(t, float64(0), progress.EstimatedRatioTokens)
}

func TestTokenUsage_Fields(t *testing.T) {
	tokenUsage := TokenUsage{
		PromptTokens:     1000,
		CompletionTokens: 2000,
		TotalTokens:      3000,
		PromptTokenDetails: PromptTokenDetails{
			CachedTokens:   500,
			UncachedTokens: 500,
		},
	}

	assert.Equal(t, int64(1000), tokenUsage.PromptTokens)
	assert.Equal(t, int64(2000), tokenUsage.CompletionTokens)
	assert.Equal(t, int64(3000), tokenUsage.TotalTokens)
	assert.Equal(t, int64(500), tokenUsage.PromptTokenDetails.CachedTokens)
	assert.Equal(t, int64(500), tokenUsage.PromptTokenDetails.UncachedTokens)
}

func TestSkillInfo_Fields(t *testing.T) {
	skillInfo := &SkillInfo{
		Type: "tool",
		Name: "search",
		Args: []Arg{
			{Name: "query", Value: "test", Type: "string"},
		},
		Checked: true,
	}

	assert.Equal(t, "tool", skillInfo.Type)
	assert.Equal(t, "search", skillInfo.Name)
	assert.Len(t, skillInfo.Args, 1)
	assert.True(t, skillInfo.Checked)
}

func TestArg_Fields(t *testing.T) {
	arg := Arg{
		Name:  "param1",
		Value: "value1",
		Type:  "string",
	}

	assert.Equal(t, "param1", arg.Name)
	assert.Equal(t, "value1", arg.Value)
	assert.Equal(t, "string", arg.Type)
}
