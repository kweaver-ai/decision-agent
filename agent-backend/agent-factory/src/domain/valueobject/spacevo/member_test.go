package spacevo

import (
	"encoding/json"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/stretchr/testify/assert"
)

func TestMemberUniq_StructFields(t *testing.T) {
	t.Parallel()

	t.Run("creates MemberUniq with values", func(t *testing.T) {
		t.Parallel()

		m := MemberUniq{
			ObjType: cenum.OrgObjTypeUser,
			ObjID:   "member-123",
		}

		assert.Equal(t, cenum.OrgObjTypeUser, m.ObjType)
		assert.Equal(t, "member-123", m.ObjID)
	})

	t.Run("creates empty MemberUniq", func(t *testing.T) {
		t.Parallel()

		m := MemberUniq{}

		assert.Empty(t, m.ObjID)
	})
}

func TestMemberAssoc_StructFields(t *testing.T) {
	t.Parallel()

	t.Run("creates MemberAssoc with values", func(t *testing.T) {
		t.Parallel()

		ma := MemberAssoc{
			MemberUniq: MemberUniq{
				ObjType: cenum.OrgObjTypeUser,
				ObjID:   "member-123",
			},
			AssocID: 456,
		}

		assert.Equal(t, cenum.OrgObjTypeUser, ma.ObjType)
		assert.Equal(t, "member-123", ma.ObjID)
		assert.Equal(t, int64(456), ma.AssocID)
	})

	t.Run("serializes to JSON", func(t *testing.T) {
		t.Parallel()

		ma := MemberAssoc{
			MemberUniq: MemberUniq{
				ObjType: cenum.OrgObjTypeUser,
				ObjID:   "member-123",
			},
			AssocID: 789,
		}

		data, err := json.Marshal(ma)
		assert.NoError(t, err)
		assert.Contains(t, string(data), "\"obj_id\":\"member-123\"")
	})
}
