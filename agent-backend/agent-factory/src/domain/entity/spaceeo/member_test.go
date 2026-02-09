package spaceeo

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
)

func TestSpaceMember_NewSpaceMember(t *testing.T) {
	member := &SpaceMember{
		SpaceMemberPo: dapo.SpaceMemberPo{
			ID: 123,
		},
		ObjName: "Test Organization",
	}

	assert.NotNil(t, member)
	assert.Equal(t, int64(123), member.ID)
	assert.Equal(t, "Test Organization", member.ObjName)
}

func TestSpaceMember_EmptyMember(t *testing.T) {
	member := &SpaceMember{}

	assert.NotNil(t, member)
	assert.Empty(t, member.ObjName)
}

func TestSpaceMember_WithNilPo(t *testing.T) {
	member := &SpaceMember{
		ObjName: "Test",
	}

	assert.NotNil(t, member)
	assert.Equal(t, "Test", member.ObjName)
}
