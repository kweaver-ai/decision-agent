package spaceresp

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/spacevo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/space/spacereq"
	"github.com/stretchr/testify/assert"
)

func TestNewAddResourcesResp(t *testing.T) {
	t.Parallel()

	resp := NewAddResourcesResp()

	assert.NotNil(t, resp)
	assert.NotNil(t, resp.Success)
	assert.NotNil(t, resp.Failed)
	assert.IsType(t, &AddResourcesResp{}, resp)
}

func TestAddResourcesResp_StructFields(t *testing.T) {
	t.Parallel()

	success := []*spacevo.ResourceAssoc{
		{
			ResourceUniq: spacevo.ResourceUniq{
				ResourceType: cdaenum.ResourceTypeDataAgent,
				ResourceID:   "agent-1",
			},
			AssocID: 1,
		},
	}
	failed := NewAddResourcesFailed()
	failed.ResourceAlreadyExists = []*spacereq.SpaceResourceReq{
		{
			ResourceType: cdaenum.ResourceTypeDataAgent,
			ResourceID:   "agent-2",
		},
	}

	resp := AddResourcesResp{
		Success: success,
		Failed:  failed,
	}

	assert.Len(t, resp.Success, 1)
	assert.NotNil(t, resp.Failed)
	assert.Len(t, resp.Failed.ResourceAlreadyExists, 1)
}

func TestAddResourcesResp_Empty(t *testing.T) {
	t.Parallel()

	resp := AddResourcesResp{}

	assert.Nil(t, resp.Success)
	assert.Nil(t, resp.Failed)
}

func TestNewAddResourcesFailed(t *testing.T) {
	t.Parallel()

	failed := NewAddResourcesFailed()

	assert.NotNil(t, failed)
	assert.NotNil(t, failed.ResourceAlreadyExists)
	assert.IsType(t, &AddResourcesFailed{}, failed)
}

func TestAddResourcesFailed_StructFields(t *testing.T) {
	t.Parallel()

	resources := []*spacereq.SpaceResourceReq{
		{
			ResourceType: cdaenum.ResourceTypeDataAgent,
			ResourceID:   "agent-1",
		},
		{
			ResourceType: cdaenum.ResourceTypeDataAgent,
			ResourceID:   "agent-2",
		},
	}

	failed := AddResourcesFailed{
		ResourceAlreadyExists: resources,
	}

	assert.Len(t, failed.ResourceAlreadyExists, 2)
	assert.Equal(t, cdaenum.ResourceTypeDataAgent, failed.ResourceAlreadyExists[0].ResourceType)
	assert.Equal(t, cdaenum.ResourceTypeDataAgent, failed.ResourceAlreadyExists[1].ResourceType)
}

func TestAddResourcesFailed_Empty(t *testing.T) {
	t.Parallel()

	failed := AddResourcesFailed{}

	assert.Nil(t, failed.ResourceAlreadyExists)
}

func TestAddResourcesResp_WithAllSuccess(t *testing.T) {
	t.Parallel()

	success := []*spacevo.ResourceAssoc{
		{
			ResourceUniq: spacevo.ResourceUniq{
				ResourceType: cdaenum.ResourceTypeDataAgent,
				ResourceID:   "agent-1",
			},
			AssocID: 1,
		},
		{
			ResourceUniq: spacevo.ResourceUniq{
				ResourceType: cdaenum.ResourceTypeDataAgent,
				ResourceID:   "agent-2",
			},
			AssocID: 2,
		},
	}

	resp := AddResourcesResp{
		Success: success,
		Failed:  NewAddResourcesFailed(),
	}

	assert.Len(t, resp.Success, 2)
	assert.Equal(t, int64(1), resp.Success[0].AssocID)
	assert.Equal(t, int64(2), resp.Success[1].AssocID)
}

func TestAddResourcesResp_WithAllFailed(t *testing.T) {
	t.Parallel()

	failed := NewAddResourcesFailed()
	failed.ResourceAlreadyExists = []*spacereq.SpaceResourceReq{
		{
			ResourceType: cdaenum.ResourceTypeDataAgent,
			ResourceID:   "agent-existing",
		},
	}

	resp := AddResourcesResp{
		Success: []*spacevo.ResourceAssoc{},
		Failed:  failed,
	}

	assert.Len(t, resp.Success, 0)
	assert.Len(t, resp.Failed.ResourceAlreadyExists, 1)
}

func TestAddResourcesFailed_WithDifferentResourceTypes(t *testing.T) {
	t.Parallel()

	resources := []*spacereq.SpaceResourceReq{
		{
			ResourceType: cdaenum.ResourceTypeDataAgent,
			ResourceID:   "agent-1",
		},
		{
			ResourceType: cdaenum.ResourceTypeDataAgentTpl,
			ResourceID:   "tpl-1",
		},
	}

	failed := AddResourcesFailed{
		ResourceAlreadyExists: resources,
	}

	assert.Len(t, failed.ResourceAlreadyExists, 2)
	assert.Equal(t, cdaenum.ResourceTypeDataAgent, failed.ResourceAlreadyExists[0].ResourceType)
	assert.Equal(t, cdaenum.ResourceTypeDataAgentTpl, failed.ResourceAlreadyExists[1].ResourceType)
}

func TestAddResourcesResp_WithMixedResults(t *testing.T) {
	t.Parallel()

	success := []*spacevo.ResourceAssoc{
		{
			ResourceUniq: spacevo.ResourceUniq{
				ResourceType: cdaenum.ResourceTypeDataAgent,
				ResourceID:   "agent-new",
			},
			AssocID: 1,
		},
	}

	failed := NewAddResourcesFailed()
	failed.ResourceAlreadyExists = []*spacereq.SpaceResourceReq{
		{
			ResourceType: cdaenum.ResourceTypeDataAgent,
			ResourceID:   "agent-existing",
		},
	}

	resp := AddResourcesResp{
		Success: success,
		Failed:  failed,
	}

	assert.Len(t, resp.Success, 1)
	assert.Len(t, resp.Failed.ResourceAlreadyExists, 1)
}

func TestAddResourcesResp_WithMultipleResources(t *testing.T) {
	t.Parallel()

	success := []*spacevo.ResourceAssoc{
		{
			ResourceUniq: spacevo.ResourceUniq{
				ResourceType: cdaenum.ResourceTypeDataAgent,
				ResourceID:   "agent-1",
			},
			AssocID: 1,
		},
		{
			ResourceUniq: spacevo.ResourceUniq{
				ResourceType: cdaenum.ResourceTypeDataAgent,
				ResourceID:   "agent-2",
			},
			AssocID: 2,
		},
		{
			ResourceUniq: spacevo.ResourceUniq{
				ResourceType: cdaenum.ResourceTypeDataAgent,
				ResourceID:   "agent-3",
			},
			AssocID: 3,
		},
	}

	resp := AddResourcesResp{
		Success: success,
		Failed:  NewAddResourcesFailed(),
	}

	assert.Len(t, resp.Success, 3)
}
