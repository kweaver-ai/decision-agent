package spacevo

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/stretchr/testify/assert"
)

func TestMemberUniq_New(t *testing.T) {
	member := &MemberUniq{
		ObjType: cenum.OrgObjTypeUser,
		ObjID:   "user-123",
	}

	assert.NotNil(t, member)
	assert.Equal(t, cenum.OrgObjTypeUser, member.ObjType)
	assert.Equal(t, "user-123", member.ObjID)
}

func TestMemberUn_EmptyFields(t *testing.T) {
	member := &MemberUniq{}

	assert.NotNil(t, member)
	assert.Empty(t, member.ObjID)
}

func TestMemberAssoc_New(t *testing.T) {
	assoc := &MemberAssoc{
		MemberUniq: MemberUniq{
			ObjType: cenum.OrgObjTypeGroup,
			ObjID:   "group-456",
		},
		AssocID: 1001,
	}

	assert.NotNil(t, assoc)
	assert.Equal(t, cenum.OrgObjTypeGroup, assoc.ObjType)
	assert.Equal(t, "group-456", assoc.ObjID)
	assert.Equal(t, int64(1001), assoc.AssocID)
}

func TestMemberAssoc_EmptyFields(t *testing.T) {
	assoc := &MemberAssoc{}

	assert.NotNil(t, assoc)
	assert.Empty(t, assoc.ObjID)
	assert.Equal(t, int64(0), assoc.AssocID)
}

func TestMemberAssoc_WithLargeAssocID(t *testing.T) {
	assoc := &MemberAssoc{
		MemberUniq: MemberUniq{
			ObjType: cenum.OrgObjTypeUser,
			ObjID:   "user-789",
		},
		AssocID: 9223372036854775807,
	}

	assert.Equal(t, int64(9223372036854775807), assoc.AssocID)
}
