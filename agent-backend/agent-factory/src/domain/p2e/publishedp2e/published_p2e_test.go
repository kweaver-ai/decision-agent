package publishedp2e

import (
	"context"
	"os"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/locale"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
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

func TestPublishedAgent_WithoutUnmarshalConfig(t *testing.T) {
	ctx := context.Background()

	po := &dapo.PublishedJoinPo{
		ReleasePartPo: dapo.ReleasePartPo{
			ReleaseID:   "release-1",
			PublishedBy: "user1",
			Version:     "1.0",
		},
		DataAgentPo: dapo.DataAgentPo{
			ID:   "agent1",
			Name: "Test Agent",
			Key:  "test-agent",
		},
	}

	eo, err := PublishedAgent(ctx, po, false)

	require.NoError(t, err)
	assert.NotNil(t, eo)
	assert.Equal(t, "release-1", eo.ReleaseID)
	assert.Equal(t, "user1", eo.PublishedBy)
	assert.Equal(t, "agent1", eo.ID)
	assert.Equal(t, "Test Agent", eo.Name)
	// Config is nil when isUnmarshalConfig is false and po.Config is empty
	assert.Nil(t, eo.Config)
}

func TestPublishedAgent_WithUnmarshalConfig_NoConfig(t *testing.T) {
	ctx := context.Background()

	po := &dapo.PublishedJoinPo{
		ReleasePartPo: dapo.ReleasePartPo{
			ReleaseID:   "release-1",
			PublishedBy: "user1",
			Version:     "1.0",
			// No AgentConfig provided
		},
		DataAgentPo: dapo.DataAgentPo{
			ID:   "agent1",
			Name: "Test Agent",
			Key:  "test-agent",
		},
	}

	eo, err := PublishedAgent(ctx, po, true)

	require.NoError(t, err)
	assert.NotNil(t, eo)
	// Config remains nil when there's no config to unmarshal
	assert.Nil(t, eo.Config)
}

func TestPublishedAgent_WithProfile(t *testing.T) {
	ctx := context.Background()

	profile := "test profile"
	po := &dapo.PublishedJoinPo{
		ReleasePartPo: dapo.ReleasePartPo{
			ReleaseID:   "release-1",
			PublishedBy: "user1",
			Version:     "1.0",
		},
		DataAgentPo: dapo.DataAgentPo{
			ID:      "agent1",
			Name:    "Test Agent",
			Key:     "test-agent",
			Profile: &profile,
		},
	}

	eo, err := PublishedAgent(ctx, po, false)

	require.NoError(t, err)
	assert.NotNil(t, eo)
	assert.NotNil(t, eo.Profile)
	assert.Equal(t, "test profile", *eo.Profile)
}

func TestPublishedAgents_EmptyList(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	pos := []*dapo.PublishedJoinPo{}

	eos, err := PublishedAgents(ctx, pos, nil, false)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 0)
}

func TestPublishedAgents_SingleAgent(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)

	pos := []*dapo.PublishedJoinPo{
		{
			ReleasePartPo: dapo.ReleasePartPo{
				ReleaseID:   "release-1",
				PublishedBy: "user1",
				Version:     "1.0",
			},
			DataAgentPo: dapo.DataAgentPo{
				ID:   "agent1",
				Name: "Test Agent",
				Key:  "test-agent",
			},
		},
	}

	eos, err := PublishedAgents(ctx, pos, nil, false)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	assert.Equal(t, "user1_name", eos[0].PublishedByName)
}

func TestPublishedAgents_MultipleAgents(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)

	pos := []*dapo.PublishedJoinPo{
		{
			ReleasePartPo: dapo.ReleasePartPo{
				ReleaseID:   "release-1",
				PublishedBy: "user1",
				Version:     "1.0",
			},
			DataAgentPo: dapo.DataAgentPo{
				ID:   "agent1",
				Name: "Agent 1",
				Key:  "agent-1",
			},
		},
		{
			ReleasePartPo: dapo.ReleasePartPo{
				ReleaseID:   "release-2",
				PublishedBy: "user2",
				Version:     "1.0",
			},
			DataAgentPo: dapo.DataAgentPo{
				ID:   "agent2",
				Name: "Agent 2",
				Key:  "agent-2",
			},
		},
	}

	eos, err := PublishedAgents(ctx, pos, nil, false)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 2)
	assert.Equal(t, "user1_name", eos[0].PublishedByName)
	assert.Equal(t, "user2_name", eos[1].PublishedByName)
}

func TestPublishedTplListEo_Simple(t *testing.T) {
	ctx := context.Background()

	po := &dapo.PublishedTplPo{
		ID:         1,
		Key:        "test-tpl",
		Name:       "Test Template",
		PublishedBy: "user1",
	}

	eo, err := PublishedTplListEo(ctx, po)

	require.NoError(t, err)
	assert.NotNil(t, eo)
	assert.Equal(t, int64(1), eo.ID)
	assert.Equal(t, "test-tpl", eo.Key)
	assert.Equal(t, "Test Template", eo.Name)
	assert.Equal(t, "user1", eo.PublishedBy)
}

func TestPublishedTplListEos_EmptyList(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	pos := []*dapo.PublishedTplPo{}

	eos, err := PublishedTplListEos(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 0)
}

func TestPublishedTplListEos_SingleTpl(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)

	pos := []*dapo.PublishedTplPo{
		{ID: 1, Key: "test-tpl", Name: "Test Template", PublishedBy: "user1"},
	}

	eos, err := PublishedTplListEos(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	assert.Equal(t, "user1_name", eos[0].PublishedByName)
}

func TestPublishedTplListEos_MultipleTpls(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)

	pos := []*dapo.PublishedTplPo{
		{ID: 1, Key: "tpl-1", Name: "Template 1", PublishedBy: "user1"},
		{ID: 2, Key: "tpl-2", Name: "Template 2", PublishedBy: "user2"},
		{ID: 3, Key: "tpl-3", Name: "Template 3", PublishedBy: "user3"},
	}

	eos, err := PublishedTplListEos(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 3)
	assert.Equal(t, "user1_name", eos[0].PublishedByName)
	assert.Equal(t, "user2_name", eos[1].PublishedByName)
	assert.Equal(t, "user3_name", eos[2].PublishedByName)
}
