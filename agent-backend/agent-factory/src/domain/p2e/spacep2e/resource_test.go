package spacep2e

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/spaceeo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestSpaceResource(t *testing.T) {
	ctx := context.Background()

	tests := []struct {
		name    string
		po      *dapo.SpaceResourcePo
		wantErr bool
		checkEO func(t *testing.T, eo *spaceeo.SpaceResource)
	}{
		{
			name: "valid space resource PO",
			po: &dapo.SpaceResourcePo{
				ID:           1,
				SpaceID:      "space-1",
				SpaceKey:     "space-key-1",
				ResourceID:   "agent-1",
				ResourceType: cdaenum.ResourceTypeDataAgent,
			},
			wantErr: false,
			checkEO: func(t *testing.T, eo *spaceeo.SpaceResource) {
				assert.NotNil(t, eo)
				assert.Equal(t, int64(1), eo.ID)
				assert.Equal(t, "space-1", eo.SpaceID)
				assert.Equal(t, "space-key-1", eo.SpaceKey)
				assert.Equal(t, "agent-1", eo.ResourceID)
				assert.Equal(t, cdaenum.ResourceTypeDataAgent, eo.ResourceType)
			},
		},
		{
			name: "space resource with minimal fields",
			po: &dapo.SpaceResourcePo{
				ID:           2,
				SpaceID:      "space-2",
				ResourceID:   "agent-2",
				ResourceType: cdaenum.ResourceTypeDataAgent,
			},
			wantErr: false,
			checkEO: func(t *testing.T, eo *spaceeo.SpaceResource) {
				assert.NotNil(t, eo)
				assert.Equal(t, int64(2), eo.ID)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			eo, err := SpaceResource(ctx, tt.po)
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				require.NoError(t, err)
				if tt.checkEO != nil {
					tt.checkEO(t, eo)
				}
			}
		})
	}
}
