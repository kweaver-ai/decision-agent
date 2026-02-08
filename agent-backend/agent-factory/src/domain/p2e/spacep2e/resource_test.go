package spacep2e

import (
	"context"
	"os"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/spaceeo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iumacc/httpaccmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/umcmp/umtypes"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestSpaceResource(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)

	tests := []struct {
		name    string
		po      *dapo.SpaceResourcePo
		wantErr bool
		checkEO func(t *testing.T, eo *spaceeo.SpaceResource)
	}{
		{
			name: "valid space resource PO",
			po: &dapo.SpaceResourcePo{
				ID:           1,
				SpaceID:      "space-1",
				SpaceKey:     "space-key-1",
				ResourceID:   "agent-1",
				ResourceType: cdaenum.ResourceTypeDataAgent,
			},
			wantErr: false,
			checkEO: func(t *testing.T, eo *spaceeo.SpaceResource) {
				assert.NotNil(t, eo)
				assert.Equal(t, int64(1), eo.ID)
				assert.Equal(t, "space-1", eo.SpaceID)
				assert.Equal(t, "space-key-1", eo.SpaceKey)
				assert.Equal(t, "agent-1", eo.ResourceID)
				assert.Equal(t, cdaenum.ResourceTypeDataAgent, eo.ResourceType)
			},
		},
		{
			name: "space resource with minimal fields",
			po: &dapo.SpaceResourcePo{
				ID:           2,
				SpaceID:      "space-2",
				ResourceID:   "agent-2",
				ResourceType: cdaenum.ResourceTypeDataAgent,
			},
			wantErr: false,
			checkEO: func(t *testing.T, eo *spaceeo.SpaceResource) {
				assert.NotNil(t, eo)
				assert.Equal(t, int64(2), eo.ID)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			eo, err := SpaceResource(ctx, tt.po)
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				require.NoError(t, err)
				if tt.checkEO != nil {
					tt.checkEO(t, eo)
				}
			}
		})
	}
}

func TestSpaceResources_EmptyList(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	pos := []*dapo.SpaceResourcePo{}
	releaseAgentPoMap := map[string]*dapo.PublishedJoinPo{}

	eos, err := SpaceResources(ctx, pos, releaseAgentPoMap, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 0)
}

func TestSpaceResources_WithValidPublishedAgent(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)

	pos := []*dapo.SpaceResourcePo{
		{
			ID:           1,
			SpaceID:      "space-1",
			SpaceKey:     "space-key-1",
			ResourceID:   "agent-1",
			ResourceType: cdaenum.ResourceTypeDataAgent,
		},
	}

	releaseAgentPoMap := map[string]*dapo.PublishedJoinPo{
		"agent-1": {
			ReleasePartPo: dapo.ReleasePartPo{
				PublishedBy: "user-1",
			},
			DataAgentPo: dapo.DataAgentPo{
				ID:   "agent-1",
				Name: "Test Agent",
				Key:  "test-agent",
			},
		},
	}

	eos, err := SpaceResources(ctx, pos, releaseAgentPoMap, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	assert.Equal(t, "Test Agent", eos[0].ResourceName)
	assert.Equal(t, "user-1_name", eos[0].PublishedAgentInfo.PublishedByName)
	assert.NotNil(t, eos[0].PublishedAgentInfo)
}

func TestSpaceResources_FilterNonDataAgent(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)

	pos := []*dapo.SpaceResourcePo{
		{
			ID:           1,
			SpaceID:      "space-1",
			ResourceID:   "agent-1",
			ResourceType: cdaenum.ResourceTypeDataAgent,
		},
	}

	releaseAgentPoMap := map[string]*dapo.PublishedJoinPo{}

	eos, err := SpaceResources(ctx, pos, releaseAgentPoMap, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 0) // Should be filtered out because no published agent exists
}

func TestSpaceResources_MultipleAgents(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)

	pos := []*dapo.SpaceResourcePo{
		{ID: 1, SpaceID: "space-1", ResourceID: "agent-1", ResourceType: cdaenum.ResourceTypeDataAgent},
		{ID: 2, SpaceID: "space-1", ResourceID: "agent-2", ResourceType: cdaenum.ResourceTypeDataAgent},
		{ID: 3, SpaceID: "space-1", ResourceID: "agent-3", ResourceType: cdaenum.ResourceTypeDataAgent},
	}

	releaseAgentPoMap := map[string]*dapo.PublishedJoinPo{
		"agent-1": {
			ReleasePartPo: dapo.ReleasePartPo{PublishedBy: "user-1"},
			DataAgentPo:   dapo.DataAgentPo{ID: "agent-1", Name: "Agent 1"},
		},
		"agent-2": {
			ReleasePartPo: dapo.ReleasePartPo{PublishedBy: "user-2"},
			DataAgentPo:   dapo.DataAgentPo{ID: "agent-2", Name: "Agent 2"},
		},
		"agent-3": {
			ReleasePartPo: dapo.ReleasePartPo{PublishedBy: "user-3"},
			DataAgentPo:   dapo.DataAgentPo{ID: "agent-3", Name: "Agent 3"},
		},
	}

	eos, err := SpaceResources(ctx, pos, releaseAgentPoMap, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 3)
	assert.Equal(t, "Agent 1", eos[0].ResourceName)
	assert.Equal(t, "Agent 2", eos[1].ResourceName)
	assert.Equal(t, "Agent 3", eos[2].ResourceName)
}

func TestSpaceResources_WithUnknownPublishedBy(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)

	pos := []*dapo.SpaceResourcePo{
		{
			ID:           1,
			SpaceID:      "space-1",
			ResourceID:   "agent-1",
			ResourceType: cdaenum.ResourceTypeDataAgent,
		},
	}

	releaseAgentPoMap := map[string]*dapo.PublishedJoinPo{
		"agent-1": {
			ReleasePartPo: dapo.ReleasePartPo{
				PublishedBy: "unknown-user", // This user won't be in the user name map
			},
			DataAgentPo: dapo.DataAgentPo{
				ID:   "agent-1",
				Name: "Test Agent",
			},
		},
	}

	eos, err := SpaceResources(ctx, pos, releaseAgentPoMap, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	// Should use unknown user name from locale
	assert.NotEmpty(t, eos[0].PublishedAgentInfo.PublishedByName)
}

func TestSpaceResources_NonLocalDevMode(t *testing.T) {
	// Temporarily unset local dev mode for this test
	originalValue := os.Getenv("AGENT_FACTORY_LOCAL_DEV")
	os.Unsetenv("AGENT_FACTORY_LOCAL_DEV")
	defer func() {
		if originalValue != "" {
			os.Setenv("AGENT_FACTORY_LOCAL_DEV", originalValue)
		}
	}()

	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockUmHttp := httpaccmock.NewMockUmHttpAcc(ctrl)

	pos := []*dapo.SpaceResourcePo{
		{
			ID:           1,
			SpaceID:      "space-1",
			SpaceKey:     "space-key-1",
			ResourceID:   "agent-1",
			ResourceType: cdaenum.ResourceTypeDataAgent,
		},
	}

	releaseAgentPoMap := map[string]*dapo.PublishedJoinPo{
		"agent-1": {
			ReleasePartPo: dapo.ReleasePartPo{
				PublishedBy: "user-1",
			},
			DataAgentPo: dapo.DataAgentPo{
				ID:   "agent-1",
				Name: "Test Agent",
			},
		},
	}

	// Expect GetOsnNames to be called in non-local dev mode
	osnInfoMap := umtypes.NewOsnInfoMapS()
	osnInfoMap.UserNameMap["user-1"] = "Real User 1"
	mockUmHttp.EXPECT().GetOsnNames(ctx, gomock.Any()).Return(osnInfoMap, nil)

	eos, err := SpaceResources(ctx, pos, releaseAgentPoMap, mockUmHttp)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	// In non-local dev mode, real user names should be used
	assert.Equal(t, "Real User 1", eos[0].PublishedAgentInfo.PublishedByName)
}
