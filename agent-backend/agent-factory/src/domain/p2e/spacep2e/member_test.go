package spacep2e

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/spaceeo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestSpaceMember(t *testing.T) {
	ctx := context.Background()

	tests := []struct {
		name    string
		po      *dapo.SpaceMemberPo
		wantErr bool
		checkEO func(t *testing.T, eo *spaceeo.SpaceMember)
	}{
		{
			name: "valid space member PO",
			po: &dapo.SpaceMemberPo{
				ID:       1,
				SpaceID:  "space-1",
				SpaceKey: "space-key-1",
				ObjType:  cenum.OrgObjTypeUser,
				ObjID:    "user-1",
			},
			wantErr: false,
			checkEO: func(t *testing.T, eo *spaceeo.SpaceMember) {
				assert.Equal(t, int64(1), eo.ID)
				assert.Equal(t, "space-1", eo.SpaceID)
				assert.Equal(t, "space-key-1", eo.SpaceKey)
				assert.Equal(t, cenum.OrgObjTypeUser, eo.ObjType)
				assert.Equal(t, "user-1", eo.ObjID)
			},
		},
		{
			name: "space member with department",
			po: &dapo.SpaceMemberPo{
				ID:       2,
				SpaceID:  "space-1",
				ObjType:  cenum.OrgObjTypeDep,
				ObjID:    "dept-1",
			},
			wantErr: false,
			checkEO: func(t *testing.T, eo *spaceeo.SpaceMember) {
				assert.Equal(t, int64(2), eo.ID)
				assert.Equal(t, cenum.OrgObjTypeDep, eo.ObjType)
			},
		},
		{
			name: "space member with group",
			po: &dapo.SpaceMemberPo{
				ID:       3,
				SpaceID:  "space-1",
				ObjType:  cenum.OrgObjTypeGroup,
				ObjID:    "group-1",
			},
			wantErr: false,
			checkEO: func(t *testing.T, eo *spaceeo.SpaceMember) {
				assert.Equal(t, int64(3), eo.ID)
				assert.Equal(t, cenum.OrgObjTypeGroup, eo.ObjType)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			eo, err := SpaceMember(ctx, tt.po)
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
