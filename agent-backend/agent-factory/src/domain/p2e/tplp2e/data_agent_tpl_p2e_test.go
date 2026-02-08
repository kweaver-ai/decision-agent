package tplp2e

import (
	"context"
	"errors"
	"os"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/locale"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
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

	// Initialize locale (only once)
	locale.Register()

	// Run tests
	code := m.Run()
	os.Exit(code)
}

func TestDataAgentTpl_Simple(t *testing.T) {
	ctx := context.Background()
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockProductRepo := idbaccessmock.NewMockIProductRepo(ctrl)

	po := &dapo.DataAgentTplPo{
		ID:         1,
		Name:       "Test Template",
		Key:        "test-template",
		ProductKey: "test-product",
	}

	// Return an empty product po to simulate not found
	productPo := &dapo.ProductPo{}
	mockProductRepo.EXPECT().GetByKey(ctx, "test-product").Return(productPo, nil)

	eo, err := DataAgentTpl(ctx, po, mockProductRepo)
	require.NoError(t, err)
	assert.NotNil(t, eo)
	assert.Equal(t, int64(1), eo.ID)
	assert.Equal(t, "Test Template", eo.Name)
	assert.Equal(t, "test-template", eo.Key)
}

func TestDataAgentTpl_WithProduct(t *testing.T) {
	ctx := context.Background()
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockProductRepo := idbaccessmock.NewMockIProductRepo(ctrl)

	po := &dapo.DataAgentTplPo{
		ID:         1,
		Name:       "Test Template",
		Key:        "test-template",
		ProductKey: "test-product",
	}

	productPo := &dapo.ProductPo{
		Key: "test-product",
		Name: "Test Product",
	}

	mockProductRepo.EXPECT().GetByKey(ctx, "test-product").Return(productPo, nil)

	eo, err := DataAgentTpl(ctx, po, mockProductRepo)
	require.NoError(t, err)
	assert.NotNil(t, eo)
	assert.Equal(t, "Test Product", eo.ProductName)
}

func TestDataAgentTpl_WithConfig(t *testing.T) {
	ctx := context.Background()
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockProductRepo := idbaccessmock.NewMockIProductRepo(ctrl)

	configJSON := `{"profile":"test profile"}`
	po := &dapo.DataAgentTplPo{
		ID:         1,
		Name:       "Test Template",
		Key:        "test-template",
		ProductKey: "test-product",
		Config:     configJSON,
	}

	// Return an empty product po
	productPo := &dapo.ProductPo{}
	mockProductRepo.EXPECT().GetByKey(ctx, "test-product").Return(productPo, nil)

	eo, err := DataAgentTpl(ctx, po, mockProductRepo)
	require.NoError(t, err)
	assert.NotNil(t, eo)
	assert.NotNil(t, eo.Config)
}

func TestDataAgentTpl_InvalidConfig(t *testing.T) {
	ctx := context.Background()
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockProductRepo := idbaccessmock.NewMockIProductRepo(ctrl)

	invalidJSON := `{invalid json`
	po := &dapo.DataAgentTplPo{
		ID:         1,
		Name:       "Test Template",
		Key:        "test-template",
		ProductKey: "test-product",
		Config:     invalidJSON,
	}

	// Config is unmarshaled BEFORE product lookup, so we don't need to expect GetByKey call
	// because the function will return early due to invalid JSON

	eo, err := DataAgentTpl(ctx, po, mockProductRepo)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "DataAgentTpl unmarshal config error")
	_ = eo // EO may be non-nil even on error
}

func TestDataAgentTpl_ProductRepoError(t *testing.T) {
	ctx := context.Background()
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockProductRepo := idbaccessmock.NewMockIProductRepo(ctrl)

	po := &dapo.DataAgentTplPo{
		ID:         1,
		Name:       "Test Template",
		Key:        "test-template",
		ProductKey: "test-product",
	}

	// Return a non-nil error that's not "sql not found"
	mockProductRepo.EXPECT().GetByKey(ctx, "test-product").Return(nil, errors.New("database connection failed"))

	eo, err := DataAgentTpl(ctx, po, mockProductRepo)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "get product name error")
	_ = eo // EO may be non-nil even on error
}

func TestDataAgentTpl_NoProductKey(t *testing.T) {
	ctx := context.Background()
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockProductRepo := idbaccessmock.NewMockIProductRepo(ctrl)

	po := &dapo.DataAgentTplPo{
		ID:         1,
		Name:       "Test Template",
		Key:        "test-template",
		ProductKey: "", // Empty product key
	}

	// Should not call GetByKey when ProductKey is empty
	eo, err := DataAgentTpl(ctx, po, mockProductRepo)
	require.NoError(t, err)
	assert.NotNil(t, eo)
	assert.Equal(t, int64(1), eo.ID)
}

func TestAgentTplListEos_EmptyList(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	pos := []*dapo.DataAgentTplPo{}

	eos, err := AgentTplListEos(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 0)
}

func TestAgentTplListEos_SingleTpl(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)

	pos := []*dapo.DataAgentTplPo{
		{ID: 1, Name: "Template 1", Key: "tpl-1", CreatedBy: "user1", UpdatedBy: "user2"},
	}

	eos, err := AgentTplListEos(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	assert.Equal(t, "user1_name", eos[0].CreatedByName)
	assert.Equal(t, "user2_name", eos[0].UpdatedByName)
}

func TestAgentTplListEos_MultipleTpls(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)

	pos := []*dapo.DataAgentTplPo{
		{ID: 1, Name: "Template 1", Key: "tpl-1", CreatedBy: "user1", UpdatedBy: "user2"},
		{ID: 2, Name: "Template 2", Key: "tpl-2", CreatedBy: "user3", UpdatedBy: "user4"},
		{ID: 3, Name: "Template 3", Key: "tpl-3", CreatedBy: "user5", UpdatedBy: "user6"},
	}

	eos, err := AgentTplListEos(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 3)
	assert.Equal(t, "user1_name", eos[0].CreatedByName)
	assert.Equal(t, "user2_name", eos[0].UpdatedByName)
	assert.Equal(t, "user3_name", eos[1].CreatedByName)
	assert.Equal(t, "user4_name", eos[1].UpdatedByName)
	assert.Equal(t, "user5_name", eos[2].CreatedByName)
	assert.Equal(t, "user6_name", eos[2].UpdatedByName)
}

func TestAgentTplListEos_WithEmptyCreatedBy(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)

	pos := []*dapo.DataAgentTplPo{
		{ID: 1, Name: "Template 1", Key: "tpl-1", CreatedBy: "", UpdatedBy: "user1"},
	}

	eos, err := AgentTplListEos(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	assert.Empty(t, eos[0].CreatedByName)
	assert.Equal(t, "user1_name", eos[0].UpdatedByName)
}

func TestAgentTplListEos_WithPublishedBy(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)

	// Create a string pointer for PublishedBy
	publishedBy := "publisher1"

	pos := []*dapo.DataAgentTplPo{
		{ID: 1, Name: "Template 1", Key: "tpl-1", CreatedBy: "user1", UpdatedBy: "user2", PublishedBy: &publishedBy},
	}

	eos, err := AgentTplListEos(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	assert.Equal(t, "user1_name", eos[0].CreatedByName)
	assert.Equal(t, "user2_name", eos[0].UpdatedByName)
	assert.Equal(t, "publisher1_name", eos[0].PublishedByName)
}

func TestAgentTplListEos_NonLocalDevMode(t *testing.T) {
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

	pos := []*dapo.DataAgentTplPo{
		{ID: 1, Name: "Template 1", Key: "tpl-1", CreatedBy: "user1", UpdatedBy: "user2"},
	}

	// Expect GetOsnNames to be called in non-local dev mode
	osnInfoMap := umtypes.NewOsnInfoMapS()
	osnInfoMap.UserNameMap["user1"] = "Real User 1"
	osnInfoMap.UserNameMap["user2"] = "Real User 2"
	mockUmHttp.EXPECT().GetOsnNames(ctx, gomock.Any()).Return(osnInfoMap, nil)

	eos, err := AgentTplListEos(ctx, pos, mockUmHttp)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	// In non-local dev mode, real user names should be used
	assert.Equal(t, "Real User 1", eos[0].CreatedByName)
	assert.Equal(t, "Real User 2", eos[0].UpdatedByName)
}

func TestAgentTplListEos_UnknownUserName(t *testing.T) {
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

	pos := []*dapo.DataAgentTplPo{
		{ID: 1, Name: "Template 1", Key: "tpl-1", CreatedBy: "unknown_user", UpdatedBy: "user2"},
	}

	// Return user info map that doesn't include "unknown_user"
	osnInfoMap := umtypes.NewOsnInfoMapS()
	osnInfoMap.UserNameMap["user2"] = "Real User 2"
	mockUmHttp.EXPECT().GetOsnNames(ctx, gomock.Any()).Return(osnInfoMap, nil)

	eos, err := AgentTplListEos(ctx, pos, mockUmHttp)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	// Unknown user should get the "unknown" placeholder
	assert.NotEmpty(t, eos[0].CreatedByName)
	assert.Equal(t, "Real User 2", eos[0].UpdatedByName)
}

func TestAgentTplListEos_NonLocalDevModeError(t *testing.T) {
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

	pos := []*dapo.DataAgentTplPo{
		{ID: 1, Name: "Template 1", Key: "tpl-1", CreatedBy: "user1", UpdatedBy: "user2"},
	}

	// Expect GetOsnNames to return an error
	mockUmHttp.EXPECT().GetOsnNames(ctx, gomock.Any()).Return(nil, errors.New("network error"))

	eos, err := AgentTplListEos(ctx, pos, mockUmHttp)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "network error")
	// eos may be non-nil but empty slice on error
	assert.Empty(t, eos)
}
