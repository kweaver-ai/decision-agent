package personalspacep2e

import (
	"context"
	"errors"
	"os"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/locale"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iumacc/httpaccmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/umcmp/umtypes"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestMain(m *testing.M) {
	// Setup environment for local dev mode (only once)
	os.Setenv("SERVICE_NAME", "AGENT_FACTORY")
	os.Setenv("AGENT_FACTORY_LOCAL_DEV", "true")
	os.Setenv("I18N_MODE_UT", "true")

	// Initialize locale (only once)
	locale.Register()

	// Run tests
	code := m.Run()
	os.Exit(code)
}

func TestAgentsListForPersonalSpace_Simple(t *testing.T) {
	ctx := context.Background()

	po := &dapo.DataAgentPo{
		ID:         "agent1",
		Name:       "Test Agent",
		Key:        "test-agent",
		ProductKey: "product1",
		CreatedBy:  "user1",
		UpdatedBy:  "user2",
	}

	eo, err := AgentsListForPersonalSpace(ctx, po)
	require.NoError(t, err)
	assert.NotNil(t, eo)
	assert.Equal(t, "agent1", eo.ID)
	assert.Equal(t, "Test Agent", eo.Name)
	assert.Equal(t, "test-agent", eo.Key)
	assert.Equal(t, "product1", eo.ProductKey)
	assert.Equal(t, "user1", eo.CreatedBy)
	assert.Equal(t, "user2", eo.UpdatedBy)
}

func TestAgentsListForPersonalSpace_WithProfile(t *testing.T) {
	ctx := context.Background()

	profile := "test profile"
	po := &dapo.DataAgentPo{
		ID:         "agent1",
		Name:       "Test Agent",
		Profile:    &profile,
		CreatedBy:  "user1",
		UpdatedBy:  "user1",
	}

	eo, err := AgentsListForPersonalSpace(ctx, po)
	require.NoError(t, err)
	assert.NotNil(t, eo)
	assert.Equal(t, "agent1", eo.ID)
	assert.NotNil(t, eo.Profile)
	assert.Equal(t, "test profile", *eo.Profile)
}

func TestAgentsListForPersonalSpace_EmptyPo(t *testing.T) {
	ctx := context.Background()

	po := &dapo.DataAgentPo{}

	eo, err := AgentsListForPersonalSpace(ctx, po)
	require.NoError(t, err)
	assert.NotNil(t, eo)
}

func TestAgentsListForPersonalSpaces_EmptyList(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	pos := []*dapo.DataAgentPo{}

	eos, err := AgentsListForPersonalSpaces(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 0)
}

func TestAgentsListForPersonalSpaces_SingleAgent(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)

	pos := []*dapo.DataAgentPo{
		{ID: "agent1", Name: "Test Agent", Key: "test-agent", ProductKey: "product1", CreatedBy: "user1", UpdatedBy: "user2"},
	}

	eos, err := AgentsListForPersonalSpaces(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	assert.Equal(t, "agent1", eos[0].ID)
	assert.Equal(t, "user1_name", eos[0].CreatedByName)
	assert.Equal(t, "user2_name", eos[0].UpdatedByName)
}

func TestAgentsListForPersonalSpaces_MultipleAgents(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)

	pos := []*dapo.DataAgentPo{
		{ID: "agent1", Name: "Agent 1", Key: "agent-1", ProductKey: "product1", CreatedBy: "user1", UpdatedBy: "user2"},
		{ID: "agent2", Name: "Agent 2", Key: "agent-2", ProductKey: "product1", CreatedBy: "user3", UpdatedBy: "user4"},
		{ID: "agent3", Name: "Agent 3", Key: "agent-3", ProductKey: "product1", CreatedBy: "user5", UpdatedBy: "user6"},
	}

	eos, err := AgentsListForPersonalSpaces(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 3)
	assert.Equal(t, "agent1", eos[0].ID)
	assert.Equal(t, "agent2", eos[1].ID)
	assert.Equal(t, "agent3", eos[2].ID)
	assert.Equal(t, "user1_name", eos[0].CreatedByName)
	assert.Equal(t, "user2_name", eos[0].UpdatedByName)
	assert.Equal(t, "user3_name", eos[1].CreatedByName)
	assert.Equal(t, "user4_name", eos[1].UpdatedByName)
	assert.Equal(t, "user5_name", eos[2].CreatedByName)
	assert.Equal(t, "user6_name", eos[2].UpdatedByName)
}

func TestAgentsListForPersonalSpaces_WithEmptyCreatedBy(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)

	pos := []*dapo.DataAgentPo{
		{ID: "agent1", Name: "Agent 1", Key: "agent-1", ProductKey: "product1", CreatedBy: "", UpdatedBy: "user1"},
	}

	eos, err := AgentsListForPersonalSpaces(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	assert.Empty(t, eos[0].CreatedByName)
	assert.Equal(t, "user1_name", eos[0].UpdatedByName)
}

func TestAgentsListForPersonalSpaces_WithSameUsers(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)

	pos := []*dapo.DataAgentPo{
		{ID: "agent1", Name: "Agent 1", Key: "agent-1", ProductKey: "product1", CreatedBy: "user1", UpdatedBy: "user1"},
		{ID: "agent2", Name: "Agent 2", Key: "agent-2", ProductKey: "product1", CreatedBy: "user1", UpdatedBy: "user1"},
	}

	eos, err := AgentsListForPersonalSpaces(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 2)
	assert.Equal(t, "user1_name", eos[0].CreatedByName)
	assert.Equal(t, "user1_name", eos[0].UpdatedByName)
	assert.Equal(t, "user1_name", eos[1].CreatedByName)
	assert.Equal(t, "user1_name", eos[1].UpdatedByName)
}

func TestAgentsListForPersonalSpaces_NonLocalDevMode(t *testing.T) {
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

	pos := []*dapo.DataAgentPo{
		{ID: "agent1", Name: "Test Agent", Key: "test-agent", ProductKey: "product1", CreatedBy: "user1", UpdatedBy: "user2"},
	}

	// Expect GetOsnNames to be called in non-local dev mode
	osnInfoMap := umtypes.NewOsnInfoMapS()
	osnInfoMap.UserNameMap["user1"] = "Real User 1"
	osnInfoMap.UserNameMap["user2"] = "Real User 2"
	mockUmHttp.EXPECT().GetOsnNames(ctx, gomock.Any()).Return(osnInfoMap, nil)

	eos, err := AgentsListForPersonalSpaces(ctx, pos, mockUmHttp)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	// In non-local dev mode, real user names should be used
	assert.Equal(t, "Real User 1", eos[0].CreatedByName)
	assert.Equal(t, "Real User 2", eos[0].UpdatedByName)
}

func TestAgentsListForPersonalSpaces_UnknownUserName(t *testing.T) {
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

	pos := []*dapo.DataAgentPo{
		{ID: "agent1", Name: "Test Agent", Key: "test-agent", ProductKey: "product1", CreatedBy: "unknown_user", UpdatedBy: "user2"},
	}

	// Return user info map that doesn't include "unknown_user"
	osnInfoMap := umtypes.NewOsnInfoMapS()
	osnInfoMap.UserNameMap["user2"] = "Real User 2"
	mockUmHttp.EXPECT().GetOsnNames(ctx, gomock.Any()).Return(osnInfoMap, nil)

	eos, err := AgentsListForPersonalSpaces(ctx, pos, mockUmHttp)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	// Unknown user should get the "unknown" placeholder
	assert.NotEmpty(t, eos[0].CreatedByName)
	assert.Equal(t, "Real User 2", eos[0].UpdatedByName)
}

func TestAgentsListForPersonalSpaces_NonLocalDevModeError(t *testing.T) {
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

	pos := []*dapo.DataAgentPo{
		{ID: "agent1", Name: "Test Agent", Key: "test-agent", ProductKey: "product1", CreatedBy: "user1", UpdatedBy: "user2"},
	}

	// Expect GetOsnNames to return an error
	mockUmHttp.EXPECT().GetOsnNames(ctx, gomock.Any()).Return(nil, errors.New("network error"))

	eos, err := AgentsListForPersonalSpaces(ctx, pos, mockUmHttp)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "network error")
	// eos may be non-nil but empty slice on error
	assert.Empty(t, eos)
}
