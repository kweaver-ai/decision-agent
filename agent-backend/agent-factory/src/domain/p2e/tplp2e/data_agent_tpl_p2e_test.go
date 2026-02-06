package tplp2e

import (
	"context"
	"errors"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

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
