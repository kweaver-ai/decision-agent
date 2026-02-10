package spaceresp

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/spacevo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/space/spacereq"
	"github.com/stretchr/testify/assert"
)

func TestNewAddMembersResp(t *testing.T) {
	resp := NewAddMembersResp()

	assert.NotNil(t, resp)
	assert.NotNil(t, resp.Success)
	assert.NotNil(t, resp.Failed)
	assert.IsType(t, &AddMembersResp{}, resp)
}

func TestAddMembersResp_StructFields(t *testing.T) {
	success := []*spacevo.MemberAssoc{
		{
			MemberUniq: spacevo.MemberUniq{
				ObjType: cenum.OrgObjTypeUser,
				ObjID:   "user-1",
			},
			AssocID: 1,
		},
	}
	failed := NewAddMemberFailed()
	failed.MemberAlreadyExists = []*spacereq.SpaceMemberReq{
		{
			ObjType: cenum.OrgObjTypeUser,
			ObjID:   "user-2",
		},
	}

	resp := AddMembersResp{
		Success: success,
		Failed:  failed,
	}

	assert.Len(t, resp.Success, 1)
	assert.NotNil(t, resp.Failed)
	assert.Len(t, resp.Failed.MemberAlreadyExists, 1)
}

func TestAddMembersResp_Empty(t *testing.T) {
	resp := AddMembersResp{}

	assert.Nil(t, resp.Success)
	assert.Nil(t, resp.Failed)
}

func TestNewAddMemberFailed(t *testing.T) {
	failed := NewAddMemberFailed()

	assert.NotNil(t, failed)
	assert.NotNil(t, failed.MemberAlreadyExists)
	assert.IsType(t, &AddMemberFailed{}, failed)
}

func TestAddMemberFailed_StructFields(t *testing.T) {
	members := []*spacereq.SpaceMemberReq{
		{
			ObjType: cenum.OrgObjTypeUser,
			ObjID:   "user-1",
		},
		{
			ObjType: cenum.OrgObjTypeDep,
			ObjID:   "dept-1",
		},
	}

	failed := AddMemberFailed{
		MemberAlreadyExists: members,
	}

	assert.Len(t, failed.MemberAlreadyExists, 2)
	assert.Equal(t, cenum.OrgObjTypeUser, failed.MemberAlreadyExists[0].ObjType)
	assert.Equal(t, cenum.OrgObjTypeDep, failed.MemberAlreadyExists[1].ObjType)
}

func TestAddMemberFailed_Empty(t *testing.T) {
	failed := AddMemberFailed{}

	assert.Nil(t, failed.MemberAlreadyExists)
}

func TestAddMembersResp_WithAllSuccess(t *testing.T) {
	success := []*spacevo.MemberAssoc{
		{
			MemberUniq: spacevo.MemberUniq{
				ObjType: cenum.OrgObjTypeUser,
				ObjID:   "user-1",
			},
			AssocID: 1,
		},
		{
			MemberUniq: spacevo.MemberUniq{
				ObjType: cenum.OrgObjTypeGroup,
				ObjID:   "group-1",
			},
			AssocID: 2,
		},
	}

	resp := AddMembersResp{
		Success: success,
		Failed:  NewAddMemberFailed(),
	}

	assert.Len(t, resp.Success, 2)
	assert.Equal(t, int64(1), resp.Success[0].AssocID)
	assert.Equal(t, int64(2), resp.Success[1].AssocID)
}

func TestAddMembersResp_WithAllFailed(t *testing.T) {
	failed := NewAddMemberFailed()
	failed.MemberAlreadyExists = []*spacereq.SpaceMemberReq{
		{
			ObjType: cenum.OrgObjTypeUser,
			ObjID:   "user-existing",
		},
	}

	resp := AddMembersResp{
		Success: []*spacevo.MemberAssoc{},
		Failed:  failed,
	}

	assert.Len(t, resp.Success, 0)
	assert.Len(t, resp.Failed.MemberAlreadyExists, 1)
}

func TestAddMemberFailed_WithDifferentMemberTypes(t *testing.T) {
	members := []*spacereq.SpaceMemberReq{
		{
			ObjType: cenum.OrgObjTypeUser,
			ObjID:   "user-1",
		},
		{
			ObjType: cenum.OrgObjTypeDep,
			ObjID:   "dept-1",
		},
		{
			ObjType: cenum.OrgObjTypeGroup,
			ObjID:   "group-1",
		},
	}

	failed := AddMemberFailed{
		MemberAlreadyExists: members,
	}

	assert.Len(t, failed.MemberAlreadyExists, 3)
}

func TestAddMembersResp_WithMixedResults(t *testing.T) {
	success := []*spacevo.MemberAssoc{
		{
			MemberUniq: spacevo.MemberUniq{
				ObjType: cenum.OrgObjTypeUser,
				ObjID:   "user-new",
			},
			AssocID: 1,
		},
	}

	failed := NewAddMemberFailed()
	failed.MemberAlreadyExists = []*spacereq.SpaceMemberReq{
		{
			ObjType: cenum.OrgObjTypeUser,
			ObjID:   "user-existing",
		},
	}

	resp := AddMembersResp{
		Success: success,
		Failed:  failed,
	}

	assert.Len(t, resp.Success, 1)
	assert.Len(t, resp.Failed.MemberAlreadyExists, 1)
}
