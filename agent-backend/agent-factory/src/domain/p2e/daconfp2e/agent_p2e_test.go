package daconfp2e

import (
	"context"
	"errors"
	"os"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/locale"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/daconfeo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/daenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/cenvhelper"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
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

	// Re-init cenvhelper so SERVICE_NAME & LOCAL_DEV take effect
	// (init() runs before TestMain, so env vars set here need a re-init)
	cenvhelper.InitEnvForTest()

	// Initialize locale (only once)
	locale.Register()

	// Run tests
	code := m.Run()
	os.Exit(code)
}

func TestDataAgent(t *testing.T) {
	ctx := context.Background()

	builtInYes := cdaenum.BuiltInYes

	tests := []struct {
		name    string
		po      *dapo.DataAgentPo
		wantErr bool
		checkEo func(t *testing.T, eo *daconfeo.DataAgent)
	}{
		{
			name: "valid po with config",
			po: &dapo.DataAgentPo{
				ID:         "1",
				Key:        "test-agent",
				Name:       "Test Agent",
				ProductKey: "test-product",
				Config:     `{"input":{"fields":[{"name":"field1","type":"text"}]}}`,
			},
			wantErr: false,
			checkEo: func(t *testing.T, eo *daconfeo.DataAgent) {
				assert.NotNil(t, eo)
				assert.Equal(t, "1", eo.ID)
				assert.Equal(t, "test-agent", eo.Key)
				assert.Equal(t, "Test Agent", eo.Name)
				assert.NotNil(t, eo.Config)
				assert.NotNil(t, eo.Config.Input)
			},
		},
		{
			name: "valid po with empty config",
			po: &dapo.DataAgentPo{
				ID:         "1",
				Key:        "test-agent",
				Name:       "Test Agent",
				ProductKey: "test-product",
				Config:     "",
			},
			wantErr: false,
			checkEo: func(t *testing.T, eo *daconfeo.DataAgent) {
				assert.NotNil(t, eo)
				assert.NotNil(t, eo.Config)
			},
		},
		{
			name: "valid po with full config",
			po: &dapo.DataAgentPo{
				ID:         "1",
				Key:        "test-agent",
				Name:       "Test Agent",
				ProductKey: "test-product",
				CreatedBy:  "user-1",
				UpdatedBy:  "user-2",
				Config: `{
					"input": {
						"fields": [
							{"name": "question", "type": "text"}
						]
					},
					"output": {
						"output_1": {
							"name": "answer",
							"type": "text"
						}
					},
					"llms": [],
					"memory": {"enabled": false}
				}`,
			},
			wantErr: false,
			checkEo: func(t *testing.T, eo *daconfeo.DataAgent) {
				assert.NotNil(t, eo)
				assert.Equal(t, "user-1", eo.CreatedBy)
				assert.Equal(t, "user-2", eo.UpdatedBy)
				assert.NotNil(t, eo.Config)
				assert.NotNil(t, eo.Config.Input)
				assert.NotNil(t, eo.Config.Output)
			},
		},
		{
			name: "valid po with all fields",
			po: &dapo.DataAgentPo{
				ID:              "1",
				Key:             "test-agent",
				Name:            "Test Agent",
				Profile:         strPtr("test profile"),
				ProductKey:      "test-product",
				AvatarType:      cdaenum.AvatarTypeBuiltIn,
				Avatar:          "🤖",
				Status:          cdaenum.StatusPublished,
				IsBuiltIn:       &builtInYes,
				CreatedAt:       100,
				UpdatedAt:       200,
				CreatedBy:       "user-1",
				UpdatedBy:       "user-2",
				Config:          `{"input":{"fields":[{"name":"field1","type":"text"}]}}`,
				CreatedType:     daenum.AgentCreatedTypeCreate,
				CreateFrom:      "from-test",
			},
			wantErr: false,
			checkEo: func(t *testing.T, eo *daconfeo.DataAgent) {
				assert.NotNil(t, eo)
				assert.Equal(t, "test-agent", eo.Key)
				assert.Equal(t, "Test Agent", eo.Name)
				assert.Equal(t, "test profile", *eo.Profile)
				assert.Equal(t, cdaenum.AvatarTypeBuiltIn, eo.AvatarType)
				assert.Equal(t, "🤖", eo.Avatar)
				assert.Equal(t, cdaenum.StatusPublished, eo.Status)
				assert.True(t, eo.IsBuiltInBool())
			},
		},
		{
			name: "invalid config json",
			po: &dapo.DataAgentPo{
				ID:     "1",
				Key:    "test-agent",
				Name:   "Test Agent",
				Config: `{invalid json}`,
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			eo, err := DataAgent(ctx, tt.po)
			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				if tt.checkEo != nil {
					tt.checkEo(t, eo)
				}
			}
		})
	}
}

func TestDataAgentSimple(t *testing.T) {
	ctx := context.Background()

	tests := []struct {
		name    string
		po      *dapo.DataAgentPo
		wantErr bool
		checkEo func(t *testing.T, eo *daconfeo.DataAgent)
	}{
		{
			name: "valid po with config",
			po: &dapo.DataAgentPo{
				ID:     "1",
				Key:    "test-agent",
				Name:   "Test Agent",
				Config: `{"input":{"fields":[{"name":"field1","type":"text"}]}}`,
			},
			wantErr: false,
			checkEo: func(t *testing.T, eo *daconfeo.DataAgent) {
				assert.NotNil(t, eo)
				assert.Equal(t, "1", eo.ID)
				assert.Equal(t, "test-agent", eo.Key)
				assert.NotNil(t, eo.Config)
				assert.NotNil(t, eo.Config.Input)
			},
		},
		{
			name: "valid po with empty config",
			po: &dapo.DataAgentPo{
				ID:   "1",
				Key:  "test-agent",
				Name: "Test Agent",
				Config: "",
			},
			wantErr: false,
			checkEo: func(t *testing.T, eo *daconfeo.DataAgent) {
				assert.NotNil(t, eo)
				assert.NotNil(t, eo.Config)
			},
		},
		{
			name: "invalid config json",
			po: &dapo.DataAgentPo{
				ID:     "1",
				Key:    "test-agent",
				Name:   "Test Agent",
				Config: `{invalid json}`,
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			eo, err := DataAgentSimple(ctx, tt.po)
			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				if tt.checkEo != nil {
					tt.checkEo(t, eo)
				}
			}
		})
	}
}

func TestDataAgent_Equals_DataAgentSimple(t *testing.T) {
	ctx := context.Background()

	// Create a valid PO
	po := &dapo.DataAgentPo{
		ID:     "1",
		Key:    "test-agent",
		Name:   "Test Agent",
		Config: `{"input":{"fields":[{"name":"question","type":"text"}]}}`,
	}

	// Test that both functions produce the same result
	eo1, err1 := DataAgent(ctx, po)
	eo2, err2 := DataAgentSimple(ctx, po)

	require.NoError(t, err1)
	require.NoError(t, err2)

	assert.Equal(t, eo1.ID, eo2.ID)
	assert.Equal(t, eo1.Key, eo2.Key)
	assert.Equal(t, eo1.Name, eo2.Name)
}

// Helper function
func strPtr(s string) *string {
	return &s
}

func TestDataAgents_EmptyList(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockProductRepo := idbaccessmock.NewMockIProductRepo(ctrl)
	pos := []*dapo.DataAgentPo{}

	// Expect GetByNameMapByKeys to be called with empty list
	mockProductRepo.EXPECT().GetByNameMapByKeys(ctx, []string{}).Return(map[string]string{}, nil)

	eos, err := DataAgents(ctx, pos, mockProductRepo, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 0)
}

func TestDataAgents_SingleAgent(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockProductRepo := idbaccessmock.NewMockIProductRepo(ctrl)
	pos := []*dapo.DataAgentPo{
		{ID: "1", Key: "test-agent", Name: "Test Agent", ProductKey: "test-product", CreatedBy: "user1", UpdatedBy: "user2"},
	}

	// Expect GetByNameMapByKeys to be called
	productMap := map[string]string{"test-product": "Test Product"}
	mockProductRepo.EXPECT().GetByNameMapByKeys(ctx, []string{"test-product"}).Return(productMap, nil)

	eos, err := DataAgents(ctx, pos, mockProductRepo, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	assert.Equal(t, "user1_name", eos[0].CreatedByName)
	assert.Equal(t, "user2_name", eos[0].UpdatedByName)
	assert.Equal(t, "Test Product", eos[0].ProductName)
}

func TestDataAgents_MultipleAgents(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockProductRepo := idbaccessmock.NewMockIProductRepo(ctrl)
	pos := []*dapo.DataAgentPo{
		{ID: "1", Key: "agent-1", Name: "Agent 1", ProductKey: "product-1", CreatedBy: "user1", UpdatedBy: "user2"},
		{ID: "2", Key: "agent-2", Name: "Agent 2", ProductKey: "product-2", CreatedBy: "user3", UpdatedBy: "user4"},
		{ID: "3", Key: "agent-3", Name: "Agent 3", ProductKey: "product-1", CreatedBy: "user5", UpdatedBy: "user6"},
	}

	// Expect GetByNameMapByKeys to be called with unique product keys
	productMap := map[string]string{"product-1": "Product 1", "product-2": "Product 2"}
	mockProductRepo.EXPECT().GetByNameMapByKeys(ctx, []string{"product-1", "product-2", "product-1"}).Return(productMap, nil)

	eos, err := DataAgents(ctx, pos, mockProductRepo, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 3)
	assert.Equal(t, "user1_name", eos[0].CreatedByName)
	assert.Equal(t, "user2_name", eos[0].UpdatedByName)
	assert.Equal(t, "Product 1", eos[0].ProductName)
	assert.Equal(t, "Product 1", eos[2].ProductName)
}

func TestDataAgents_WithEmptyCreatedBy(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockProductRepo := idbaccessmock.NewMockIProductRepo(ctrl)
	pos := []*dapo.DataAgentPo{
		{ID: "1", Key: "test-agent", Name: "Test Agent", ProductKey: "test-product", CreatedBy: "", UpdatedBy: "user1"},
	}

	productMap := map[string]string{"test-product": "Test Product"}
	mockProductRepo.EXPECT().GetByNameMapByKeys(ctx, []string{"test-product"}).Return(productMap, nil)

	eos, err := DataAgents(ctx, pos, mockProductRepo, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	assert.Empty(t, eos[0].CreatedByName)
	assert.Equal(t, "user1_name", eos[0].UpdatedByName)
}

func TestDataAgents_WithEmptyProductKey(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockProductRepo := idbaccessmock.NewMockIProductRepo(ctrl)
	pos := []*dapo.DataAgentPo{
		{ID: "1", Key: "test-agent", Name: "Test Agent", ProductKey: "", CreatedBy: "user1", UpdatedBy: "user2"},
	}

	// When ProductKey is empty, it's still included in the productKeys list
	mockProductRepo.EXPECT().GetByNameMapByKeys(ctx, []string{""}).Return(map[string]string{}, nil)

	eos, err := DataAgents(ctx, pos, mockProductRepo, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	assert.Equal(t, "user1_name", eos[0].CreatedByName)
	assert.Equal(t, "user2_name", eos[0].UpdatedByName)
	assert.Empty(t, eos[0].ProductName) // No product name when ProductKey is empty
}

func TestDataAgents_ProductRepoError(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockProductRepo := idbaccessmock.NewMockIProductRepo(ctrl)
	pos := []*dapo.DataAgentPo{
		{ID: "1", Key: "test-agent", Name: "Test Agent", ProductKey: "test-product", CreatedBy: "user1", UpdatedBy: "user2"},
	}

	// Simulate an error from productRepo
	mockProductRepo.EXPECT().GetByNameMapByKeys(ctx, []string{"test-product"}).Return(nil, errors.New("database error"))

	_, err := DataAgents(ctx, pos, mockProductRepo, nil)

	assert.Error(t, err)
	// Note: eos may not be nil even on error, just check that error is returned
}

func TestDataAgents_InvalidConfigInBatch(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockProductRepo := idbaccessmock.NewMockIProductRepo(ctrl)
	pos := []*dapo.DataAgentPo{
		{ID: "1", Key: "test-agent", Name: "Test Agent", ProductKey: "test-product", CreatedBy: "user1", UpdatedBy: "user2"},
		{ID: "2", Key: "invalid-agent", Name: "Invalid Agent", ProductKey: "test-product", Config: `{invalid json}`},
	}

	productMap := map[string]string{"test-product": "Test Product"}
	mockProductRepo.EXPECT().GetByNameMapByKeys(ctx, []string{"test-product", "test-product"}).Return(productMap, nil)

	_, err := DataAgents(ctx, pos, mockProductRepo, nil)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "unmarshal config error")
}

func TestDataAgents_UnknownUser(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockProductRepo := idbaccessmock.NewMockIProductRepo(ctrl)

	// Create a user that will not be in the UserNameMap (using a special prefix)
	unknownUser := "unknown_user_prefix_xyz"
	pos := []*dapo.DataAgentPo{
		{ID: "1", Key: "test-agent", Name: "Test Agent", ProductKey: "test-product", CreatedBy: unknownUser, UpdatedBy: "user2"},
	}

	productMap := map[string]string{"test-product": "Test Product"}
	mockProductRepo.EXPECT().GetByNameMapByKeys(ctx, []string{"test-product"}).Return(productMap, nil)

	eos, err := DataAgents(ctx, pos, mockProductRepo, nil)

	assert.NoError(t, err)
	assert.Len(t, eos, 1)
	// The created by name should be "未知用户" (UnknownUser) from locale since the user is not in the map
	assert.NotEmpty(t, eos[0].CreatedByName)
	assert.Equal(t, "user2_name", eos[0].UpdatedByName)
}

func TestDataAgents_NonLocalDevMode(t *testing.T) {
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

	mockProductRepo := idbaccessmock.NewMockIProductRepo(ctrl)
	mockUmHttp := httpaccmock.NewMockUmHttpAcc(ctrl)

	pos := []*dapo.DataAgentPo{
		{ID: "1", Key: "test-agent", Name: "Test Agent", ProductKey: "test-product", CreatedBy: "user1", UpdatedBy: "user2"},
	}

	// Expect GetOsnNames to be called in non-local dev mode
	osnInfoMap := umtypes.NewOsnInfoMapS()
	osnInfoMap.UserNameMap["user1"] = "Real User 1"
	osnInfoMap.UserNameMap["user2"] = "Real User 2"
	mockUmHttp.EXPECT().GetOsnNames(ctx, gomock.Any()).Return(osnInfoMap, nil)

	productMap := map[string]string{"test-product": "Test Product"}
	mockProductRepo.EXPECT().GetByNameMapByKeys(ctx, []string{"test-product"}).Return(productMap, nil)

	eos, err := DataAgents(ctx, pos, mockProductRepo, mockUmHttp)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	// In non-local dev mode, real user names should be used
	assert.Equal(t, "Real User 1", eos[0].CreatedByName)
	assert.Equal(t, "Real User 2", eos[0].UpdatedByName)
	assert.Equal(t, "Test Product", eos[0].ProductName)
}
