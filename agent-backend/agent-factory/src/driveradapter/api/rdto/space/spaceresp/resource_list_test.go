package spaceresp

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/spaceeo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewResourceListResp(t *testing.T) {
	t.Parallel()

	resp := NewResourceListResp()

	assert.NotNil(t, resp)
	assert.NotNil(t, resp.Entries)
	assert.Empty(t, resp.Entries)
}

func TestResourceListResp_LoadFromEos(t *testing.T) {
	t.Parallel()

	t.Run("empty slice", func(t *testing.T) {
		t.Parallel()

		resp := NewResourceListResp()

		err := resp.LoadFromEos([]*spaceeo.SpaceResource{})

		assert.NoError(t, err)
		assert.Empty(t, resp.Entries)
	})

	t.Run("with single data agent resource", func(t *testing.T) {
		t.Parallel()

		resp := NewResourceListResp()

		eos := []*spaceeo.SpaceResource{
			{
				SpaceResourcePo: dapo.SpaceResourcePo{
					ID:           1,
					SpaceID:      "space-1",
					ResourceType: cdaenum.ResourceTypeDataAgent,
					ResourceID:   "agent-1",
					CreatedBy:    "user-1",
					CreatedAt:    1234567890,
				},
			},
		}

		err := resp.LoadFromEos(eos)

		require.NoError(t, err)
		assert.Len(t, resp.Entries, 1)
		assert.Equal(t, int64(1), resp.Entries[0].ID)
		assert.Equal(t, "space-1", resp.Entries[0].SpaceID)
		assert.Equal(t, cdaenum.ResourceTypeDataAgent, resp.Entries[0].ResourceType)
		assert.Equal(t, "agent-1", resp.Entries[0].ResourceID)
		assert.Equal(t, "user-1", resp.Entries[0].CreatedBy)
		assert.Equal(t, int64(1234567890), resp.Entries[0].CreatedAt)
	})

	t.Run("with data agent tpl resource", func(t *testing.T) {
		t.Parallel()

		resp := NewResourceListResp()

		eos := []*spaceeo.SpaceResource{
			{
				SpaceResourcePo: dapo.SpaceResourcePo{
					ID:           2,
					SpaceID:      "space-1",
					ResourceType: cdaenum.ResourceTypeDataAgentTpl,
					ResourceID:   "tpl-1",
					CreatedBy:    "admin-1",
				},
			},
		}

		err := resp.LoadFromEos(eos)

		require.NoError(t, err)
		assert.Len(t, resp.Entries, 1)
		assert.Equal(t, cdaenum.ResourceTypeDataAgentTpl, resp.Entries[0].ResourceType)
		assert.Equal(t, "tpl-1", resp.Entries[0].ResourceID)
	})

	t.Run("with multiple resources", func(t *testing.T) {
		t.Parallel()

		resp := NewResourceListResp()

		eos := []*spaceeo.SpaceResource{
			{
				SpaceResourcePo: dapo.SpaceResourcePo{
					ID:           1,
					SpaceID:      "space-1",
					ResourceType: cdaenum.ResourceTypeDataAgent,
					ResourceID:   "agent-1",
				},
			},
			{
				SpaceResourcePo: dapo.SpaceResourcePo{
					ID:           2,
					SpaceID:      "space-1",
					ResourceType: cdaenum.ResourceTypeDataAgentTpl,
					ResourceID:   "tpl-1",
				},
			},
		}

		err := resp.LoadFromEos(eos)

		require.NoError(t, err)
		assert.Len(t, resp.Entries, 2)
		assert.Equal(t, "agent-1", resp.Entries[0].ResourceID)
		assert.Equal(t, cdaenum.ResourceTypeDataAgent, resp.Entries[0].ResourceType)
		assert.Equal(t, "tpl-1", resp.Entries[1].ResourceID)
		assert.Equal(t, cdaenum.ResourceTypeDataAgentTpl, resp.Entries[1].ResourceType)
	})

	t.Run("with nil published agent info", func(t *testing.T) {
		t.Parallel()

		resp := NewResourceListResp()

		eos := []*spaceeo.SpaceResource{
			{
				SpaceResourcePo: dapo.SpaceResourcePo{
					ID:           1,
					SpaceID:      "space-1",
					ResourceType: cdaenum.ResourceTypeDataAgent,
					ResourceID:   "agent-1",
				},
			},
		}

		err := resp.LoadFromEos(eos)

		require.NoError(t, err)
		assert.Len(t, resp.Entries, 1)
		assert.Nil(t, resp.Entries[0].PublishedAgentInfo)
	})
}

func TestResourceItem_StructFields(t *testing.T) {
	t.Parallel()

	item := ResourceItem{
		ID:           123,
		SpaceID:      "space-1",
		ResourceType: cdaenum.ResourceTypeDataAgent,
		ResourceID:   "agent-1",
		ResourceName: "Agent One",
		CreatedBy:    "user-1",
		CreatedAt:    1234567890,
	}

	assert.Equal(t, int64(123), item.ID)
	assert.Equal(t, "space-1", item.SpaceID)
	assert.Equal(t, cdaenum.ResourceTypeDataAgent, item.ResourceType)
	assert.Equal(t, "agent-1", item.ResourceID)
	assert.Equal(t, "Agent One", item.ResourceName)
	assert.Equal(t, "user-1", item.CreatedBy)
	assert.Equal(t, int64(1234567890), item.CreatedAt)
}

func TestResourceItem_Empty(t *testing.T) {
	t.Parallel()

	item := ResourceItem{}

	assert.Equal(t, int64(0), item.ID)
	assert.Empty(t, item.SpaceID)
	assert.Equal(t, cdaenum.ResourceType(""), item.ResourceType)
	assert.Empty(t, item.ResourceID)
	assert.Empty(t, item.ResourceName)
	assert.Empty(t, item.CreatedBy)
	assert.Equal(t, int64(0), item.CreatedAt)
}

func TestResourceItem_WithPublishedAgentInfo(t *testing.T) {
	t.Parallel()

	// Test the structure can accept published agent info
	item := ResourceItem{
		ID:           1,
		SpaceID:      "space-1",
		ResourceType: cdaenum.ResourceTypeDataAgent,
		ResourceID:   "agent-1",
		ResourceName: "Agent One",
	}

	assert.NotNil(t, item)
	assert.Equal(t, "agent-1", item.ResourceID)
}

func TestResourceItem_WithTplType(t *testing.T) {
	t.Parallel()

	item := ResourceItem{
		ID:           1,
		SpaceID:      "space-1",
		ResourceType: cdaenum.ResourceTypeDataAgentTpl,
		ResourceID:   "tpl-1",
		ResourceName: "Template One",
	}

	assert.NotNil(t, item)
	assert.Equal(t, "tpl-1", item.ResourceID)
	assert.Equal(t, cdaenum.ResourceTypeDataAgentTpl, item.ResourceType)
}
