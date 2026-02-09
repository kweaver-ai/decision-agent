package agentfactorydto

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/daconfvalobj"
)

func TestField_StructFields(t *testing.T) {
	field := Field{
		Name: "test_field",
		Type: "string",
	}

	assert.Equal(t, "test_field", field.Name)
	assert.Equal(t, "string", field.Type)
}

func TestRewrite_StructFields(t *testing.T) {
	llmConfig := LLMConfig{
		ID:   "llm-123",
		Name: "Test LLM",
	}
	rewrite := Rewrite{
		Enable:    true,
		LLMConfig: llmConfig,
	}

	assert.True(t, rewrite.Enable)
	assert.Equal(t, "llm-123", rewrite.LLMConfig.ID)
}

func TestKg_StructFields(t *testing.T) {
	kg := Kg{
		KgID:            "kg-123",
		Fields:          []string{"field1", "field2"},
		FieldProperties: []string{"prop1"},
		OutputFields:    []string{"out1"},
	}

	assert.Equal(t, "kg-123", kg.KgID)
	assert.Len(t, kg.Fields, 2)
	assert.Contains(t, kg.Fields, "field1")
}

func TestDocField_StructFields(t *testing.T) {
	docField := DocField{
		Name:   "test_name",
		Path:   "/path/to/file",
		Source: "test_source",
	}

	assert.Equal(t, "test_name", docField.Name)
	assert.Equal(t, "/path/to/file", docField.Path)
	assert.Equal(t, "test_source", docField.Source)
}

func TestDoc_StructFields(t *testing.T) {
	doc := Doc{
		DsID:   "ds-123",
		Fields: []DocField{{Name: "field1"}},
	}

	assert.Equal(t, "ds-123", doc.DsID)
	assert.Len(t, doc.Fields, 1)
}

func TestAugment_StructFields(t *testing.T) {
	augment := Augment{
		Enable: true,
		Datasource: AugmentDatasource{
			Kg: []Kg{{KgID: "kg-1"}},
		},
	}

	assert.True(t, augment.Enable)
	assert.Len(t, augment.Datasource.Kg, 1)
}

func TestLLMConfig_StructFields(t *testing.T) {
	llmConfig := LLMConfig{
		ID:               "llm-123",
		Name:             "Test LLM",
		ModelType:        "gpt-4",
		Temperature:      0.7,
		TopP:             0.9,
		TopK:             50,
		FrequencyPenalty: 0.1,
		PresencePenalty:  0.2,
		MaxTokens:        2000,
	}

	assert.Equal(t, "llm-123", llmConfig.ID)
	assert.Equal(t, 0.7, llmConfig.Temperature)
	assert.Equal(t, 50, llmConfig.TopK)
}

func TestTempZoneConfig_StructFields(t *testing.T) {
	config := TempZoneConfig{
		Name:                    "test_zone",
		MaxFileCount:            10,
		SingleFileSizeLimit:     100,
		SingleFileSizeLimitUnit: "MB",
		SupportDataType:         []string{"pdf", "txt"},
		TempFileUseType:         "test",
	}

	assert.Equal(t, "test_zone", config.Name)
	assert.Equal(t, 10, config.MaxFileCount)
	assert.Contains(t, config.SupportDataType, "pdf")
}

func TestAgentConfigInput_StructFields(t *testing.T) {
	input := AgentConfigInput{
		Fields: []Field{{Name: "field1", Type: "string"}},
		Rewrite: Rewrite{
			Enable: true,
		},
		Augment: Augment{
			Enable: false,
		},
	}

	assert.Len(t, input.Fields, 1)
	assert.True(t, input.Rewrite.Enable)
	assert.False(t, input.Augment.Enable)
}

func TestAgentConfigOutput_StructFields(t *testing.T) {
	output := AgentConfigOutput{
		DefaultFormat: "json",
		Variables: Variable{
			AnswerVar:           "answer",
			DocRetrievalVar:     "docs",
			GraphRetrievalVar:   "graph",
			RelatedQuestionsVar: "questions",
			OtherVars:           []string{"var1", "var2"},
		},
	}

	assert.Equal(t, "json", output.DefaultFormat)
	assert.Equal(t, "answer", output.Variables.AnswerVar)
	assert.Len(t, output.Variables.OtherVars, 2)
}

func TestTool_StructFields(t *testing.T) {
	tool := Tool{
		ToolType:           "api",
		ToolName:           "Test Tool",
		ToolID:             "tool-123",
		ToolBoxID:          "box-456",
		ToolUseDescription: "Test description",
		ToolInput:          map[string]interface{}{"key": "value"},
		Intervention:       true,
	}

	assert.Equal(t, "api", tool.ToolType)
	assert.Equal(t, "tool-123", tool.ToolID)
	assert.True(t, tool.Intervention)
}

func TestOpeningRemarkConfig_StructFields(t *testing.T) {
	config := OpeningRemarkConfig{
		Type:                       "fixed",
		FixedOpeningRemark:         "Hello!",
		DynamicOpeningRemarkPrompt: "Generate greeting",
	}

	assert.Equal(t, "fixed", config.Type)
	assert.Equal(t, "Hello!", config.FixedOpeningRemark)
}

func TestPresetQuestion_StructFields(t *testing.T) {
	question := PresetQuestion{
		Question: "What is AI?",
	}

	assert.Equal(t, "What is AI?", question.Question)
}

func TestPublishInfo_StructFields(t *testing.T) {
	publishInfo := PublishInfo{
		IsAPIAgent:      1,
		IsSDKAgent:      1,
		IsSkillAgent:    0,
		IsDataFlowAgent: 0,
	}

	assert.Equal(t, 1, publishInfo.IsAPIAgent)
	assert.Equal(t, 0, publishInfo.IsSkillAgent)
}

func TestAgent_StructFields(t *testing.T) {
	agent := Agent{
		ID:           "agent-123",
		Key:          "key-456",
		IsBuiltIn:    0,
		Name:         "Test Agent",
		CategoryID:   "cat-123",
		CategoryName: "Test Category",
		Profile:      "Test profile",
		Version:      "1.0.0",
		Config:       daconfvalobj.Config{},
		AvatarType:   1,
		Avatar:       "avatar.png",
		ProductID:    100,
		ProductName:  "Test Product",
		PublishInfo: PublishInfo{
			IsAPIAgent: 1,
		},
	}

	assert.Equal(t, "agent-123", agent.ID)
	assert.Equal(t, "Test Agent", agent.Name)
	assert.Equal(t, "1.0.0", agent.Version)
	assert.Equal(t, 1, agent.PublishInfo.IsAPIAgent)
}
