package spacevo

import (
	"github.com/stretchr/testify/assert"
	"testing"
)

func TestMemberUniq(t *testing.T) {
	tests := []struct {
		name   string
		member *MemberUniq
	}{
		{
			name: "用户类型",
			member: &MemberUniq{
				ObjType: "user",
				ObjID:   "user-123",
			},
		},
		{
			name: "角色类型",
			member: &MemberUniq{
				ObjType: "role",
				ObjID:   "role-456",
			},
		},
		{
			name: "空值",
			member: &MemberUniq{
				ObjType: "",
				ObjID:   "",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.member.ObjType, tt.member.ObjType)
			assert.Equal(t, tt.member.ObjID, tt.member.ObjID)
		})
	}
}

func TestMemberAssoc(t *testing.T) {
	tests := []struct {
		name   string
		assoc  MemberAssoc
		wantID int64
	}{
		{
			name: "有效关联ID",
			assoc: MemberAssoc{
				MemberUniq: MemberUniq{
					ObjType: "user",
					ObjID:   "user-123",
				},
				AssocID: 12345,
			},
			wantID: 12345,
		},
		{
			name: "零ID",
			assoc: MemberAssoc{
				MemberUniq: MemberUniq{
					ObjType: "role",
					ObjID:   "role-456",
				},
				AssocID: 0,
			},
			wantID: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.wantID, tt.assoc.AssocID)
		})
	}
}
