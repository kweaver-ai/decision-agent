package personalspaceresp

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/daconfeo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/daenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/publishvo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
)

func TestNewAgentListItem(t *testing.T) {
	item := NewAgentListItem()

	assert.NotNil(t, item)
	assert.NotNil(t, item.PublishInfo)
}

func TestAgentListItem_StructFields(t *testing.T) {
	publishInfo := publishvo.NewListPublishInfo()

	item := &AgentListItem{
		ID:            "agent-123",
		Key:           "agent-key",
		IsBuiltIn:     1,
		IsSystemAgent: 0,
		Name:          "Test Agent",
		Profile:       "Test profile",
		Version:       "1.0.0",
		AvatarType:    1,
		Avatar:        "avatar.png",
		ProductKey:    "product-key",
		Status:        cdaenum.StatusThreeStatePublished,
		CreatedType:   daenum.AgentCreatedTypeCreate,
		UpdatedAt:     1234567890,
		UpdatedBy:     "user-1",
		UpdatedByName: "User One",
		CreatedBy:     "user-2",
		CreatedByName: "User Two",
		CreatedAt:     1234567890,
		PublishedAt:    1234567891,
		PublishInfo:    publishInfo,
	}

	assert.Equal(t, "agent-123", item.ID)
	assert.Equal(t, "agent-key", item.Key)
	assert.Equal(t, 1, item.IsBuiltIn)
	assert.Equal(t, "Test Agent", item.Name)
	assert.Equal(t, "1.0.0", item.Version)
	assert.Equal(t, cdaenum.StatusThreeStatePublished, item.Status)
}

func TestNewAgentListResp(t *testing.T) {
	resp := NewAgentListResp()

	assert.NotNil(t, resp)
	assert.NotNil(t, resp.Entries)
	assert.Empty(t, resp.Entries)
}

func TestAgentListResp_LoadFromEos_Empty(t *testing.T) {
	resp := NewAgentListResp()
	eos := []*daconfeo.DataAgent{}

	err := resp.LoadFromEos(eos, nil)

	assert.NoError(t, err)
}

func TestAgentListResp_LoadFromEos_Single(t *testing.T) {
	resp := NewAgentListResp()

	eo := &daconfeo.DataAgent{}

	err := resp.LoadFromEos([]*daconfeo.DataAgent{eo}, nil)

	assert.NoError(t, err)
	assert.Len(t, resp.Entries, 1)
}

func TestAgentListResp_LoadFromEos_Multiple(t *testing.T) {
	resp := NewAgentListResp()

	eos := []*daconfeo.DataAgent{
		{},
		{},
		{},
	}

	err := resp.LoadFromEos(eos, nil)

	assert.NoError(t, err)
	assert.Len(t, resp.Entries, 3)
}

func TestAgentListResp_LoadFromEos_WithReleaseMap(t *testing.T) {
	resp := NewAgentListResp()

	eo := &daconfeo.DataAgent{}

	releaseAgentPoMap := map[string]*dapo.PublishedJoinPo{}

	err := resp.LoadFromEos([]*daconfeo.DataAgent{eo}, releaseAgentPoMap)

	assert.NoError(t, err)
}

func TestAgentListResp_genMarkerStr_Empty(t *testing.T) {
	resp := &AgentListResp{
		Entries: []*AgentListItem{},
	}

	markerStr, err := resp.genMarkerStr()

	assert.NoError(t, err)
	assert.Empty(t, markerStr)
}

func TestAgentListResp_genMarkerStr_IsLastPage(t *testing.T) {
	resp := &AgentListResp{
		Entries: []*AgentListItem{
			{ID: "agent-1", UpdatedAt: 100},
		},
		IsLastPage: true,
	}

	markerStr, err := resp.genMarkerStr()

	assert.NoError(t, err)
	assert.Empty(t, markerStr)
}

func TestAgentListResp_genMarkerStr_WithEntries(t *testing.T) {
	resp := &AgentListResp{
		Entries: []*AgentListItem{
			{ID: "agent-1", UpdatedAt: 100},
			{ID: "agent-2", UpdatedAt: 200},
		},
	}

	markerStr, err := resp.genMarkerStr()

	assert.NoError(t, err)
	assert.NotEmpty(t, markerStr)
}

func TestAgentListResp_StructFields(t *testing.T) {
	marker := &PAListPaginationMarker{}
	resp := &AgentListResp{
		Entries:            []*AgentListItem{},
		PaginationMarkerStr: "marker-string",
		Marker:              marker,
		IsLastPage:          false,
	}

	assert.NotNil(t, resp.Entries)
	assert.Equal(t, "marker-string", resp.PaginationMarkerStr)
	assert.Equal(t, marker, resp.Marker)
	assert.False(t, resp.IsLastPage)
}
