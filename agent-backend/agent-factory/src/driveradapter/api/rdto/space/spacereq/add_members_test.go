package spacereq

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/constant/csconstant"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestAddMembersReq_GetErrMsgMap(t *testing.T) {
	t.Parallel()

	req := &AddMembersReq{}
	errMap := req.GetErrMsgMap()

	assert.NotEmpty(t, errMap)
	assert.Equal(t, `"members"不能为空`, errMap["Members.required"])
	assert.Equal(t, `"members"至少需要一个成员`, errMap["Members.min"])
}

func TestAddMembersReq_CustomCheck(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name    string
		req     *AddMembersReq
		wantErr bool
		errMsg  string
	}{
		{
			name: "empty members",
			req: &AddMembersReq{
				Members: []*SpaceMemberReq{},
			},
			wantErr: true,
			errMsg:  "成员列表不能为空",
		},
		{
			name: "valid single member",
			req: &AddMembersReq{
				Members: []*SpaceMemberReq{
					{
						ObjType: cenum.OrgObjTypeUser,
						ObjID:   "user-1",
					},
				},
			},
			wantErr: false,
		},
		{
			name: "valid multiple members",
			req: &AddMembersReq{
				Members: []*SpaceMemberReq{
					{
						ObjType: cenum.OrgObjTypeUser,
						ObjID:   "user-1",
					},
					{
						ObjType: cenum.OrgObjTypeDep,
						ObjID:   "dept-1",
					},
				},
			},
			wantErr: false,
		},
		{
			name: "invalid obj type",
			req: &AddMembersReq{
				Members: []*SpaceMemberReq{
					{
						ObjType: "invalid",
						ObjID:   "user-1",
					},
				},
			},
			wantErr: true,
			errMsg:  "无效的成员类型",
		},
		{
			name: "exceeds max members",
			req: func() *AddMembersReq {
				members := make([]*SpaceMemberReq, csconstant.MaxMemberNumInOneSpace+1)
				for i := range members {
					members[i] = &SpaceMemberReq{
						ObjType: cenum.OrgObjTypeUser,
						ObjID:   "user-" + string(rune(i)),
					}
				}
				return &AddMembersReq{Members: members}
			}(),
			wantErr: true,
			errMsg:  "成员数量超过最大限制",
		},
		{
			name: "duplicate members - should be deduplicated",
			req: &AddMembersReq{
				Members: []*SpaceMemberReq{
					{
						ObjType: cenum.OrgObjTypeUser,
						ObjID:   "user-1",
					},
					{
						ObjType: cenum.OrgObjTypeUser,
						ObjID:   "user-1",
					},
				},
			},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()

			err := tt.req.CustomCheck()
			if tt.wantErr {
				require.Error(t, err)

				if tt.errMsg != "" {
					assert.Contains(t, err.Error(), tt.errMsg)
				}
			} else {
				require.NoError(t, err)
			}
		})
	}
}

func TestAddMembersReq_ToMemberEos(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name        string
		members     []*SpaceMemberReq
		spaceID     string
		spaceKey    string
		wantErr     bool
		expectedLen int
	}{
		{
			name: "convert single member",
			members: []*SpaceMemberReq{
				{
					ObjType: cenum.OrgObjTypeUser,
					ObjID:   "user-1",
				},
			},
			spaceID:     "space-1",
			spaceKey:    "space-key-1",
			wantErr:     false,
			expectedLen: 1,
		},
		{
			name: "convert multiple members",
			members: []*SpaceMemberReq{
				{
					ObjType: cenum.OrgObjTypeUser,
					ObjID:   "user-1",
				},
				{
					ObjType: cenum.OrgObjTypeDep,
					ObjID:   "dept-1",
				},
			},
			spaceID:     "space-2",
			spaceKey:    "space-key-2",
			wantErr:     false,
			expectedLen: 2,
		},
		{
			name:        "empty members",
			members:     []*SpaceMemberReq{},
			spaceID:     "space-3",
			spaceKey:    "space-key-3",
			wantErr:     false,
			expectedLen: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()

			req := &AddMembersReq{}
			eos, err := req.ToMemberEos(tt.members, tt.spaceID, tt.spaceKey)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				assert.Len(t, eos, tt.expectedLen)
			}

			// Verify space ID and key are set correctly
			for _, eo := range eos {
				assert.Equal(t, tt.spaceID, eo.SpaceID)
				assert.Equal(t, tt.spaceKey, eo.SpaceKey)
			}
		})
	}
}

func TestAddMembersReq_StructFields(t *testing.T) {
	t.Parallel()

	req := &AddMembersReq{
		Members: []*SpaceMemberReq{
			{
				ObjType: cenum.OrgObjTypeUser,
				ObjID:   "user-1",
			},
		},
	}

	assert.NotNil(t, req.Members)
	assert.Len(t, req.Members, 1)
	assert.Equal(t, cenum.OrgObjTypeUser, req.Members[0].ObjType)
	assert.Equal(t, "user-1", req.Members[0].ObjID)
}

func TestAddMembersReq_Deduplication(t *testing.T) {
	t.Parallel()

	req := &AddMembersReq{
		Members: []*SpaceMemberReq{
			{
				ObjType: cenum.OrgObjTypeUser,
				ObjID:   "user-1",
			},
			{
				ObjType: cenum.OrgObjTypeUser,
				ObjID:   "user-1",
			},
			{
				ObjType: cenum.OrgObjTypeUser,
				ObjID:   "user-2",
			},
		},
	}

	originalLen := len(req.Members)
	err := req.CustomCheck()
	require.NoError(t, err)

	// After deduplication, should have 2 unique members
	assert.Less(t, len(req.Members), originalLen)
}
