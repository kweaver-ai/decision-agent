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

func TestDataAgentTpl(t *testing.T) {
	tests := []struct {
		name    string
		eo      *daconfeo.DataAgentTpl
		wantErr bool
		checkPO func(t *testing.T, po *dapo.DataAgentTplPo)
	}{
		{
			name: "valid template entity",
			eo: &daconfeo.DataAgentTpl{
				DataAgentTplPo: dapo.DataAgentTplPo{
					ID:     1,
					Name:   "Test Template",
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
			checkPO: func(t *testing.T, po *dapo.DataAgentTplPo) {
				assert.Equal(t, int64(1), po.ID)
				assert.Equal(t, "Test Template", po.Name)
				assert.Equal(t, cdaenum.StatusPublished, po.Status)
				assert.NotEmpty(t, po.Config, "Config should be marshaled to JSON")
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			po, err := DataAgentTpl(tt.eo)
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

func TestDataAgentTpls(t *testing.T) {
	tests := []struct {
		name    string
		eos     []*daconfeo.DataAgentTpl
		wantErr bool
		checkPOs func(t *testing.T, pos []*dapo.DataAgentTplPo)
	}{
		{
			name: "multiple valid templates",
			eos: []*daconfeo.DataAgentTpl{
				{
					DataAgentTplPo: dapo.DataAgentTplPo{
						ID:   1,
						Name: "Template 1",
					},
					Config: &daconfvalobj.Config{
						Input:  &daconfvalobj.Input{},
						Output: &daconfvalobj.Output{},
					},
				},
				{
					DataAgentTplPo: dapo.DataAgentTplPo{
						ID:   2,
						Name: "Template 2",
					},
					Config: &daconfvalobj.Config{
						Input:  &daconfvalobj.Input{},
						Output: &daconfvalobj.Output{},
					},
				},
			},
			wantErr: false,
			checkPOs: func(t *testing.T, pos []*dapo.DataAgentTplPo) {
				assert.Len(t, pos, 2)
				assert.Equal(t, int64(1), pos[0].ID)
				assert.Equal(t, int64(2), pos[1].ID)
			},
		},
		{
			name:    "empty slice",
			eos:     []*daconfeo.DataAgentTpl{},
			wantErr: false,
			checkPOs: func(t *testing.T, pos []*dapo.DataAgentTplPo) {
				assert.Len(t, pos, 0)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			pos, err := DataAgentTpls(tt.eos)
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
