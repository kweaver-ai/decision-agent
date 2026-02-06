package spacee2p

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/spaceeo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestSpaceResource(t *testing.T) {
	tests := []struct {
		name    string
		eo      *spaceeo.SpaceResource
		wantErr bool
		checkPO func(t *testing.T, po *dapo.SpaceResourcePo)
	}{
		{
			name: "valid space resource",
			eo: &spaceeo.SpaceResource{
				SpaceResourcePo: dapo.SpaceResourcePo{
					ID:           1,
					SpaceID:      "space-1",
					SpaceKey:     "space-key-1",
					ResourceID:   "agent-1",
					ResourceType: cdaenum.ResourceTypeDataAgent,
				},
			},
			wantErr: false,
			checkPO: func(t *testing.T, po *dapo.SpaceResourcePo) {
				assert.Equal(t, int64(1), po.ID)
				assert.Equal(t, "space-1", po.SpaceID)
				assert.Equal(t, "space-key-1", po.SpaceKey)
				assert.Equal(t, "agent-1", po.ResourceID)
				assert.Equal(t, cdaenum.ResourceTypeDataAgent, po.ResourceType)
			},
		},
		{
			name: "resource with minimal fields",
			eo: &spaceeo.SpaceResource{
				SpaceResourcePo: dapo.SpaceResourcePo{
					ID:           2,
					SpaceID:      "space-2",
					ResourceID:   "agent-2",
					ResourceType: cdaenum.ResourceTypeDataAgent,
				},
			},
			wantErr: false,
			checkPO: func(t *testing.T, po *dapo.SpaceResourcePo) {
				assert.Equal(t, int64(2), po.ID)
				assert.Equal(t, "space-2", po.SpaceID)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			po, err := SpaceResource(tt.eo)
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

func TestSpaceResources(t *testing.T) {
	tests := []struct {
		name    string
		eos     []*spaceeo.SpaceResource
		wantErr bool
		checkPOs func(t *testing.T, pos []*dapo.SpaceResourcePo)
	}{
		{
			name: "multiple valid resources",
			eos: []*spaceeo.SpaceResource{
				{
					SpaceResourcePo: dapo.SpaceResourcePo{
						ID:           1,
						SpaceID:      "space-1",
						ResourceID:   "agent-1",
						ResourceType: cdaenum.ResourceTypeDataAgent,
					},
				},
				{
					SpaceResourcePo: dapo.SpaceResourcePo{
						ID:           2,
						SpaceID:      "space-1",
						ResourceID:   "agent-2",
						ResourceType: cdaenum.ResourceTypeDataAgent,
					},
				},
			},
			wantErr: false,
			checkPOs: func(t *testing.T, pos []*dapo.SpaceResourcePo) {
				assert.Len(t, pos, 2)
				assert.Equal(t, int64(1), pos[0].ID)
				assert.Equal(t, int64(2), pos[1].ID)
			},
		},
		{
			name:    "empty slice",
			eos:     []*spaceeo.SpaceResource{},
			wantErr: false,
			checkPOs: func(t *testing.T, pos []*dapo.SpaceResourcePo) {
				assert.Len(t, pos, 0)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			pos, err := SpaceResources(tt.eos)
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
