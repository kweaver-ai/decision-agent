package daconfe2p

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/daconfeo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/daconfvalobj"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestDataAgent(t *testing.T) {
	tests := []struct {
		name    string
		eo      *daconfeo.DataAgent
		wantErr bool
		checkPO func(t *testing.T, po *dapo.DataAgentPo)
	}{
		{
			name: "valid entity",
			eo: &daconfeo.DataAgent{
				DataAgentPo: dapo.DataAgentPo{
					ID:     "test-id",
					Name:   "Test Agent",
					Status: cdaenum.StatusPublished,
				},
				Config: &daconfvalobj.Config{
					Input: &daconfvalobj.Input{
						Fields: daconfvalobj.Fields{
							&daconfvalobj.Field{
								Name: "field1",
								Type: cdaenum.InputFieldTypeString,
							},
						},
					},
					Output: &daconfvalobj.Output{},
				},
			},
			wantErr: false,
			checkPO: func(t *testing.T, po *dapo.DataAgentPo) {
				assert.Equal(t, "test-id", po.ID)
				assert.Equal(t, "Test Agent", po.Name)
				assert.Equal(t, cdaenum.StatusPublished, po.Status)
				assert.NotEmpty(t, po.Config, "Config should be marshaled to JSON")
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			po, err := DataAgent(tt.eo)
			if tt.wantErr {
				assert.Error(t, err)
				assert.Nil(t, po)
			} else {
				require.NoError(t, err)
				require.NotNil(t, po)
				if tt.checkPO != nil {
					tt.checkPO(t, po)
				}
			}
		})
	}
}

func TestDataAgents(t *testing.T) {
	tests := []struct {
		name    string
		eos     []*daconfeo.DataAgent
		wantErr bool
		checkPOs func(t *testing.T, pos []*dapo.DataAgentPo)
	}{
		{
			name: "multiple valid entities",
			eos: []*daconfeo.DataAgent{
				{
					DataAgentPo: dapo.DataAgentPo{
						ID:   "agent-1",
						Name: "Agent 1",
					},
					Config: &daconfvalobj.Config{
						Input:  &daconfvalobj.Input{},
						Output: &daconfvalobj.Output{},
					},
				},
				{
					DataAgentPo: dapo.DataAgentPo{
						ID:   "agent-2",
						Name: "Agent 2",
					},
					Config: &daconfvalobj.Config{
						Input:  &daconfvalobj.Input{},
						Output: &daconfvalobj.Output{},
					},
				},
			},
			wantErr: false,
			checkPOs: func(t *testing.T, pos []*dapo.DataAgentPo) {
				assert.Len(t, pos, 2)
				assert.Equal(t, "agent-1", pos[0].ID)
				assert.Equal(t, "agent-2", pos[1].ID)
			},
		},
		{
			name:    "empty slice",
			eos:     []*daconfeo.DataAgent{},
			wantErr: false,
			checkPOs: func(t *testing.T, pos []*dapo.DataAgentPo) {
				assert.Len(t, pos, 0)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			pos, err := DataAgents(tt.eos)
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				require.NoError(t, err)
				if tt.checkPOs != nil {
					tt.checkPOs(t, pos)
				}
			}
		})
	}
}

func TestDataAgent_WithNilConfig(t *testing.T) {
	eo := &daconfeo.DataAgent{
		DataAgentPo: dapo.DataAgentPo{
			ID:     "test-id",
			Name:   "Test Agent",
			Status: cdaenum.StatusPublished,
		},
		Config: nil,
	}

	po, err := DataAgent(eo)
	require.NoError(t, err)
	require.NotNil(t, po)
	assert.Equal(t, "test-id", po.ID)
}

func TestDataAgent_WithComplexConfig(t *testing.T) {
	isDefault := true
	eo := &daconfeo.DataAgent{
		DataAgentPo: dapo.DataAgentPo{
			ID:     "test-id",
			Name:   "Complex Agent",
			Status: cdaenum.StatusPublished,
		},
		Config: &daconfvalobj.Config{
			Input: &daconfvalobj.Input{
				Fields: daconfvalobj.Fields{
					&daconfvalobj.Field{
						Name: "field1",
						Type: cdaenum.InputFieldTypeString,
					},
				},
			},
			Llms: []*daconfvalobj.LlmItem{
				{
					IsDefault: isDefault,
					LlmConfig: &daconfvalobj.LlmConfig{
						Name:      "test-model",
						MaxTokens: 500,
					},
				},
			},
			IsDataFlowSetEnabled: 0,
			Output: &daconfvalobj.Output{
				DefaultFormat: cdaenum.OutputDefaultFormatMarkdown,
			},
		},
	}

	po, err := DataAgent(eo)
	require.NoError(t, err)
	require.NotNil(t, po)
	assert.Equal(t, "test-id", po.ID)
	assert.NotEmpty(t, po.Config)
}
