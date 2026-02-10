package spacee2p

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/spaceeo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestSpaceMember(t *testing.T) {
	tests := []struct {
		name    string
		eo      *spaceeo.SpaceMember
		wantErr bool
		checkPO func(t *testing.T, po *dapo.SpaceMemberPo)
	}{
		{
			name: "valid space member",
			eo: &spaceeo.SpaceMember{
				SpaceMemberPo: dapo.SpaceMemberPo{
					ID:       1,
					SpaceID:  "space-1",
					SpaceKey: "space-key-1",
					ObjType:  cenum.OrgObjTypeUser,
					ObjID:    "user-1",
				},
			},
			wantErr: false,
			checkPO: func(t *testing.T, po *dapo.SpaceMemberPo) {
				assert.Equal(t, int64(1), po.ID)
				assert.Equal(t, "space-1", po.SpaceID)
				assert.Equal(t, "space-key-1", po.SpaceKey)
				assert.Equal(t, cenum.OrgObjTypeUser, po.ObjType)
				assert.Equal(t, "user-1", po.ObjID)
			},
		},
		{
			name: "member with minimal fields",
			eo: &spaceeo.SpaceMember{
				SpaceMemberPo: dapo.SpaceMemberPo{
					ID:      2,
					SpaceID: "space-2",
					ObjType: cenum.OrgObjTypeDep,
					ObjID:   "dept-1",
				},
			},
			wantErr: false,
			checkPO: func(t *testing.T, po *dapo.SpaceMemberPo) {
				assert.Equal(t, int64(2), po.ID)
				assert.Equal(t, "space-2", po.SpaceID)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			po, err := SpaceMember(tt.eo)
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

func TestSpaceMembers(t *testing.T) {
	tests := []struct {
		name    string
		eos     []*spaceeo.SpaceMember
		wantErr bool
		checkPOs func(t *testing.T, pos []*dapo.SpaceMemberPo)
	}{
		{
			name: "multiple valid members",
			eos: []*spaceeo.SpaceMember{
				{
					SpaceMemberPo: dapo.SpaceMemberPo{
						ID:      1,
						SpaceID: "space-1",
						ObjType: cenum.OrgObjTypeUser,
						ObjID:   "user-1",
					},
				},
				{
					SpaceMemberPo: dapo.SpaceMemberPo{
						ID:      2,
						SpaceID: "space-1",
						ObjType: cenum.OrgObjTypeUser,
						ObjID:   "user-2",
					},
				},
			},
			wantErr: false,
			checkPOs: func(t *testing.T, pos []*dapo.SpaceMemberPo) {
				assert.Len(t, pos, 2)
				assert.Equal(t, int64(1), pos[0].ID)
				assert.Equal(t, int64(2), pos[1].ID)
			},
		},
		{
			name:    "empty slice",
			eos:     []*spaceeo.SpaceMember{},
			wantErr: false,
			checkPOs: func(t *testing.T, pos []*dapo.SpaceMemberPo) {
				assert.Len(t, pos, 0)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			pos, err := SpaceMembers(tt.eos)
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

func TestSpaceMembers_SingleMember(t *testing.T) {
	eos := []*spaceeo.SpaceMember{
		{
			SpaceMemberPo: dapo.SpaceMemberPo{
				ID:      1,
				SpaceID: "space-1",
				ObjType: cenum.OrgObjTypeUser,
				ObjID:   "user-1",
			},
		},
	}

	pos, err := SpaceMembers(eos)
	require.NoError(t, err)
	assert.Len(t, pos, 1)
	assert.Equal(t, int64(1), pos[0].ID)
}

func TestSpaceMember_NilEntity(t *testing.T) {
	eo := &spaceeo.SpaceMember{
		SpaceMemberPo: dapo.SpaceMemberPo{
			ID:      1,
			SpaceID: "space-1",
		},
	}

	po, err := SpaceMember(eo)
	require.NoError(t, err)
	require.NotNil(t, po)
	assert.Equal(t, int64(1), po.ID)
}

func TestSpaceMembers_AllFields(t *testing.T) {
	eo := &spaceeo.SpaceMember{
		SpaceMemberPo: dapo.SpaceMemberPo{
			ID:       1,
			SpaceID:  "space-1",
			SpaceKey: "space-key-1",
			ObjType:  cenum.OrgObjTypeUser,
			ObjID:    "user-1",
		},
	}

	po, err := SpaceMember(eo)
	require.NoError(t, err)
	assert.Equal(t, int64(1), po.ID)
	assert.Equal(t, "space-1", po.SpaceID)
}
