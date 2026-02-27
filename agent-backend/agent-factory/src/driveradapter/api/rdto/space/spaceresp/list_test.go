package spaceresp

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/spaceeo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
)

func TestNewListResp(t *testing.T) {
	t.Parallel()

	t.Run("with total", func(t *testing.T) {
		t.Parallel()

		resp := NewListResp(10)

		assert.NotNil(t, resp)
		assert.Equal(t, int64(10), resp.Total)
		assert.NotNil(t, resp.Entries)
		assert.Empty(t, resp.Entries)
	})

	t.Run("with zero total", func(t *testing.T) {
		t.Parallel()

		resp := NewListResp(0)

		assert.NotNil(t, resp)
		assert.Equal(t, int64(0), resp.Total)
		assert.Empty(t, resp.Entries)
	})

	t.Run("with negative total", func(t *testing.T) {
		t.Parallel()

		resp := NewListResp(-1)

		assert.NotNil(t, resp)
		assert.Equal(t, int64(-1), resp.Total)
		assert.Empty(t, resp.Entries)
	})
}

func TestListResp_LoadFromEos(t *testing.T) {
	t.Parallel()

	t.Run("empty slice", func(t *testing.T) {
		t.Parallel()

		resp := NewListResp(0)
		err := resp.LoadFromEos([]*spaceeo.Space{})

		assert.NoError(t, err)
		assert.Empty(t, resp.Entries)
	})

	t.Run("nil slice", func(t *testing.T) {
		t.Parallel()

		resp := NewListResp(0)
		err := resp.LoadFromEos(nil)

		assert.NoError(t, err)
		assert.Empty(t, resp.Entries)
	})

	t.Run("single space", func(t *testing.T) {
		t.Parallel()

		resp := NewListResp(1)
		eos := []*spaceeo.Space{
			{
				SpacePo: dapo.SpacePo{
					ID:        "space-1",
					Name:      "Test Space",
					Key:       "test-space",
					Profile:   "Test profile",
					CreatedAt: 1234567890,
					UpdatedAt: 1234567899,
					CreatedBy: "user-1",
					UpdatedBy: "user-1",
				},
			},
		}

		err := resp.LoadFromEos(eos)

		assert.NoError(t, err)
		assert.Len(t, resp.Entries, 1)
		assert.Equal(t, "space-1", resp.Entries[0].ID)
		assert.Equal(t, "Test Space", resp.Entries[0].Name)
		assert.Equal(t, "test-space", resp.Entries[0].Key)
		assert.Equal(t, "Test profile", resp.Entries[0].Profile)
		assert.Equal(t, int64(1234567890), resp.Entries[0].CreatedAt)
		assert.Equal(t, int64(1234567899), resp.Entries[0].UpdatedAt)
		assert.Equal(t, "user-1", resp.Entries[0].CreatedBy)
		assert.Equal(t, "user-1", resp.Entries[0].UpdatedBy)
	})

	t.Run("multiple spaces", func(t *testing.T) {
		t.Parallel()

		resp := NewListResp(2)
		eos := []*spaceeo.Space{
			{
				SpacePo: dapo.SpacePo{
					ID:        "space-1",
					Name:      "Space One",
					Key:       "space-one",
					CreatedAt: 1000000000,
				},
			},
			{
				SpacePo: dapo.SpacePo{
					ID:        "space-2",
					Name:      "Space Two",
					Key:       "space-two",
					CreatedAt: 2000000000,
				},
			},
		}

		err := resp.LoadFromEos(eos)

		assert.NoError(t, err)
		assert.Len(t, resp.Entries, 2)
		assert.Equal(t, "space-1", resp.Entries[0].ID)
		assert.Equal(t, "Space One", resp.Entries[0].Name)
		assert.Equal(t, "space-2", resp.Entries[1].ID)
		assert.Equal(t, "Space Two", resp.Entries[1].Name)
	})

	t.Run("with empty fields", func(t *testing.T) {
		t.Parallel()

		resp := NewListResp(1)
		eos := []*spaceeo.Space{
			{
				SpacePo: dapo.SpacePo{
					ID:   "space-empty",
					Name: "",
					Key:  "",
				},
			},
		}

		err := resp.LoadFromEos(eos)

		assert.NoError(t, err)
		assert.Len(t, resp.Entries, 1)
		assert.Equal(t, "space-empty", resp.Entries[0].ID)
		assert.Empty(t, resp.Entries[0].Name)
		assert.Empty(t, resp.Entries[0].Key)
	})
}

func TestListItem_StructFields(t *testing.T) {
	t.Parallel()

	item := ListItem{
		ID:            "space-1",
		Name:          "Test Space",
		Key:           "test-space",
		Profile:       "Test profile",
		CreatedAt:     1234567890,
		UpdatedAt:     1234567899,
		CreatedBy:     "user-1",
		UpdatedBy:     "user-2",
		CreatedByName: "User One",
		UpdatedByName: "User Two",
	}

	assert.Equal(t, "space-1", item.ID)
	assert.Equal(t, "Test Space", item.Name)
	assert.Equal(t, "test-space", item.Key)
	assert.Equal(t, "Test profile", item.Profile)
	assert.Equal(t, int64(1234567890), item.CreatedAt)
	assert.Equal(t, int64(1234567899), item.UpdatedAt)
	assert.Equal(t, "user-1", item.CreatedBy)
	assert.Equal(t, "user-2", item.UpdatedBy)
	assert.Equal(t, "User One", item.CreatedByName)
	assert.Equal(t, "User Two", item.UpdatedByName)
}

func TestListItem_Empty(t *testing.T) {
	t.Parallel()

	item := ListItem{}

	assert.Empty(t, item.ID)
	assert.Empty(t, item.Name)
	assert.Empty(t, item.Key)
	assert.Empty(t, item.Profile)
	assert.Equal(t, int64(0), item.CreatedAt)
	assert.Equal(t, int64(0), item.UpdatedAt)
	assert.Empty(t, item.CreatedBy)
	assert.Empty(t, item.UpdatedBy)
	assert.Empty(t, item.CreatedByName)
	assert.Empty(t, item.UpdatedByName)
}

func TestListResp_StructFields(t *testing.T) {
	t.Parallel()

	resp := ListResp{
		Entries: []*ListItem{
			{ID: "space-1", Name: "Space One"},
			{ID: "space-2", Name: "Space Two"},
		},
		Total: 2,
	}

	assert.Len(t, resp.Entries, 2)
	assert.Equal(t, int64(2), resp.Total)
	assert.Equal(t, "space-1", resp.Entries[0].ID)
	assert.Equal(t, "Space One", resp.Entries[0].Name)
	assert.Equal(t, "space-2", resp.Entries[1].ID)
	assert.Equal(t, "Space Two", resp.Entries[1].Name)
}
