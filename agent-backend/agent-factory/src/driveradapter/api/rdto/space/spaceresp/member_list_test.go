package spaceresp

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/spaceeo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewMemberListResp(t *testing.T) {
	t.Parallel()

	resp := NewMemberListResp()

	assert.NotNil(t, resp)
	assert.NotNil(t, resp.Entries)
	assert.Empty(t, resp.Entries)
}

func TestMemberListResp_LoadFromEos(t *testing.T) {
	t.Parallel()

	t.Run("empty slice", func(t *testing.T) {
		t.Parallel()

		resp := NewMemberListResp()
		ctx := context.Background()

		err := resp.LoadFromEos(ctx, []*spaceeo.SpaceMember{})

		assert.NoError(t, err)
		assert.Empty(t, resp.Entries)
	})

	t.Run("with single user member", func(t *testing.T) {
		t.Parallel()

		resp := NewMemberListResp()
		ctx := context.Background()

		eos := []*spaceeo.SpaceMember{
			{
				SpaceMemberPo: dapo.SpaceMemberPo{
					ID:        1,
					SpaceID:   "space-1",
					ObjType:   cenum.OrgObjTypeUser,
					ObjID:     "user-1",
					CreatedBy: "user-1",
					CreatedAt: 1234567890,
				},
			},
		}

		err := resp.LoadFromEos(ctx, eos)

		require.NoError(t, err)
		assert.Len(t, resp.Entries, 1)
		assert.Equal(t, int64(1), resp.Entries[0].ID)
		assert.Equal(t, "space-1", resp.Entries[0].SpaceID)
		assert.Equal(t, cenum.OrgObjTypeUser, resp.Entries[0].ObjType)
		assert.Equal(t, "user-1", resp.Entries[0].ObjID)
		assert.Equal(t, "user-1", resp.Entries[0].CreatedBy)
		assert.Equal(t, int64(1234567890), resp.Entries[0].CreatedAt)
	})

	t.Run("with dept member", func(t *testing.T) {
		t.Parallel()

		resp := NewMemberListResp()
		ctx := context.Background()

		eos := []*spaceeo.SpaceMember{
			{
				SpaceMemberPo: dapo.SpaceMemberPo{
					ID:        2,
					SpaceID:   "space-1",
					ObjType:   cenum.OrgObjTypeDep,
					ObjID:     "dept-1",
					CreatedBy: "admin-1",
				},
			},
		}

		err := resp.LoadFromEos(ctx, eos)

		require.NoError(t, err)
		assert.Len(t, resp.Entries, 1)
		assert.Equal(t, cenum.OrgObjTypeDep, resp.Entries[0].ObjType)
		assert.Equal(t, "dept-1", resp.Entries[0].ObjID)
	})

	t.Run("with user group member", func(t *testing.T) {
		t.Parallel()

		resp := NewMemberListResp()
		ctx := context.Background()

		eos := []*spaceeo.SpaceMember{
			{
				SpaceMemberPo: dapo.SpaceMemberPo{
					ID:        3,
					SpaceID:   "space-1",
					ObjType:   cenum.OrgObjTypeGroup,
					ObjID:     "group-1",
					CreatedBy: "admin-1",
				},
			},
		}

		err := resp.LoadFromEos(ctx, eos)

		require.NoError(t, err)
		assert.Len(t, resp.Entries, 1)
		assert.Equal(t, cenum.OrgObjTypeGroup, resp.Entries[0].ObjType)
		assert.Equal(t, "group-1", resp.Entries[0].ObjID)
	})

	t.Run("with multiple members", func(t *testing.T) {
		t.Parallel()

		resp := NewMemberListResp()
		ctx := context.Background()

		eos := []*spaceeo.SpaceMember{
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
		}

		err := resp.LoadFromEos(ctx, eos)

		require.NoError(t, err)
		assert.Len(t, resp.Entries, 2)
		assert.Equal(t, "user-1", resp.Entries[0].ObjID)
		assert.Equal(t, "user-2", resp.Entries[1].ObjID)
	})

	t.Run("member is owner when created by matches obj id", func(t *testing.T) {
		t.Parallel()

		resp := NewMemberListResp()
		ctx := context.Background()

		eos := []*spaceeo.SpaceMember{
			{
				SpaceMemberPo: dapo.SpaceMemberPo{
					ID:        1,
					SpaceID:   "space-1",
					ObjType:   cenum.OrgObjTypeUser,
					ObjID:     "user-1",
					CreatedBy: "user-1",
				},
			},
		}

		err := resp.LoadFromEos(ctx, eos)

		require.NoError(t, err)
		assert.True(t, resp.Entries[0].IsOwner)
	})

	t.Run("member is not owner when created by differs from obj id", func(t *testing.T) {
		t.Parallel()

		resp := NewMemberListResp()
		ctx := context.Background()

		eos := []*spaceeo.SpaceMember{
			{
				SpaceMemberPo: dapo.SpaceMemberPo{
					ID:        1,
					SpaceID:   "space-1",
					ObjType:   cenum.OrgObjTypeUser,
					ObjID:     "user-2",
					CreatedBy: "user-1",
				},
			},
		}

		err := resp.LoadFromEos(ctx, eos)

		require.NoError(t, err)
		assert.False(t, resp.Entries[0].IsOwner)
	})

	t.Run("member is myself when obj id matches current user", func(t *testing.T) {
		t.Parallel()

		resp := NewMemberListResp()

		// Create context with visitor info
		visitor := &rest.Visitor{
			ID: "user-1",
		}
		ctx := context.WithValue(context.Background(), cenum.VisitUserInfoCtxKey.String(), visitor)

		eos := []*spaceeo.SpaceMember{
			{
				SpaceMemberPo: dapo.SpaceMemberPo{
					ID:        1,
					SpaceID:   "space-1",
					ObjType:   cenum.OrgObjTypeUser,
					ObjID:     "user-1",
					CreatedBy: "admin-1",
				},
			},
		}

		err := resp.LoadFromEos(ctx, eos)

		require.NoError(t, err)
		assert.True(t, resp.Entries[0].IsMyself)
		assert.False(t, resp.Entries[0].IsOwner)
	})

	t.Run("member is not myself when obj id differs from current user", func(t *testing.T) {
		t.Parallel()

		resp := NewMemberListResp()

		// Create context with visitor info
		visitor := &rest.Visitor{
			ID: "user-2",
		}
		ctx := context.WithValue(context.Background(), cenum.VisitUserInfoCtxKey.String(), visitor)

		eos := []*spaceeo.SpaceMember{
			{
				SpaceMemberPo: dapo.SpaceMemberPo{
					ID:        1,
					SpaceID:   "space-1",
					ObjType:   cenum.OrgObjTypeUser,
					ObjID:     "user-1",
					CreatedBy: "admin-1",
				},
			},
		}

		err := resp.LoadFromEos(ctx, eos)

		require.NoError(t, err)
		assert.False(t, resp.Entries[0].IsMyself)
	})

	t.Run("dept member is not myself even when obj id matches user id", func(t *testing.T) {
		t.Parallel()

		resp := NewMemberListResp()

		// Create context with visitor info - dept should not be marked as myself
		visitor := &rest.Visitor{
			ID: "dept-1",
		}
		ctx := context.WithValue(context.Background(), cenum.VisitUserInfoCtxKey.String(), visitor)

		eos := []*spaceeo.SpaceMember{
			{
				SpaceMemberPo: dapo.SpaceMemberPo{
					ID:        1,
					SpaceID:   "space-1",
					ObjType:   cenum.OrgObjTypeDep,
					ObjID:     "dept-1",
					CreatedBy: "admin-1",
				},
			},
		}

		err := resp.LoadFromEos(ctx, eos)

		require.NoError(t, err)
		assert.False(t, resp.Entries[0].IsMyself, "Dept member should not be marked as myself")
	})

	t.Run("member is both owner and myself", func(t *testing.T) {
		t.Parallel()

		resp := NewMemberListResp()

		// Create context with visitor info matching member's ObjID and CreatedBy
		visitor := &rest.Visitor{
			ID: "user-1",
		}
		ctx := context.WithValue(context.Background(), cenum.VisitUserInfoCtxKey.String(), visitor)

		eos := []*spaceeo.SpaceMember{
			{
				SpaceMemberPo: dapo.SpaceMemberPo{
					ID:        1,
					SpaceID:   "space-1",
					ObjType:   cenum.OrgObjTypeUser,
					ObjID:     "user-1",
					CreatedBy: "user-1",
				},
			},
		}

		err := resp.LoadFromEos(ctx, eos)

		require.NoError(t, err)
		assert.True(t, resp.Entries[0].IsOwner, "Member should be owner when ObjID equals CreatedBy")
		assert.True(t, resp.Entries[0].IsMyself, "Member should be myself when ObjID equals current user")
	})
}

func TestMemberItem_StructFields(t *testing.T) {
	t.Parallel()

	item := MemberItem{
		ID:        123,
		SpaceID:   "space-1",
		ObjType:   cenum.OrgObjTypeUser,
		ObjID:     "user-1",
		ObjName:   "User One",
		CreatedBy: "admin-1",
		CreatedAt: 1234567890,
		IsOwner:   true,
		IsMyself:  true,
	}

	assert.Equal(t, int64(123), item.ID)
	assert.Equal(t, "space-1", item.SpaceID)
	assert.Equal(t, cenum.OrgObjTypeUser, item.ObjType)
	assert.Equal(t, "user-1", item.ObjID)
	assert.Equal(t, "User One", item.ObjName)
	assert.Equal(t, "admin-1", item.CreatedBy)
	assert.Equal(t, int64(1234567890), item.CreatedAt)
	assert.True(t, item.IsOwner)
	assert.True(t, item.IsMyself)
}

func TestMemberItem_Empty(t *testing.T) {
	t.Parallel()

	item := MemberItem{}

	assert.Equal(t, int64(0), item.ID)
	assert.Empty(t, item.SpaceID)
	assert.Equal(t, cenum.OrgObjType(""), item.ObjType)
	assert.Empty(t, item.ObjID)
	assert.Empty(t, item.ObjName)
	assert.Empty(t, item.CreatedBy)
	assert.Equal(t, int64(0), item.CreatedAt)
	assert.False(t, item.IsOwner)
	assert.False(t, item.IsMyself)
}
