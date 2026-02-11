package publishedsvc

import (
	"context"
	"errors"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/stretchr/testify/assert"
)

func TestPublishedSvc_PubedTplDetail_PanicsWithoutPublishedTplRepo(t *testing.T) {
	svc := &publishedSvc{
		SvcBase: service.NewSvcBase(),
	}

	ctx := context.Background()
	tplID := int64(123)

	assert.Panics(t, func() {
		_, _ = svc.PubedTplDetail(ctx, tplID)
	})
}

func TestPublishedSvc_PubedTplDetail_TemplateNotFound(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockPublishedTplRepo := idbaccessmock.NewMockIPublishedTplRepo(ctrl)
	mockProductRepo := idbaccessmock.NewMockIProductRepo(ctrl)

	svc := &publishedSvc{
		SvcBase:          service.NewSvcBase(),
		publishedTplRepo: mockPublishedTplRepo,
		productRepo:      mockProductRepo,
	}

	ctx := context.Background()
	tplID := int64(123)

	// Use chelper.IsSqlNotFound pattern - need to simulate the error
	notFoundErr := errors.New("sql: no rows in result set")
	mockPublishedTplRepo.EXPECT().GetByTplID(gomock.Any(), tplID).Return(nil, notFoundErr)

	res, err := svc.PubedTplDetail(ctx, tplID)

	assert.Error(t, err)
	assert.Nil(t, res)
}

func TestPublishedSvc_PubedTplDetail_GetByTplIDError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockPublishedTplRepo := idbaccessmock.NewMockIPublishedTplRepo(ctrl)
	mockProductRepo := idbaccessmock.NewMockIProductRepo(ctrl)

	svc := &publishedSvc{
		SvcBase:          service.NewSvcBase(),
		publishedTplRepo: mockPublishedTplRepo,
		productRepo:      mockProductRepo,
	}

	ctx := context.Background()
	tplID := int64(123)

	dbErr := errors.New("database connection failed")
	mockPublishedTplRepo.EXPECT().GetByTplID(gomock.Any(), tplID).Return(nil, dbErr)

	res, err := svc.PubedTplDetail(ctx, tplID)

	assert.Error(t, err)
	assert.Nil(t, res)
}

func TestPublishedSvc_PubedTplDetail_ConvertPanic(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockPublishedTplRepo := idbaccessmock.NewMockIPublishedTplRepo(ctrl)
	mockProductRepo := idbaccessmock.NewMockIProductRepo(ctrl)

	svc := &publishedSvc{
		SvcBase:          service.NewSvcBase(),
		publishedTplRepo: mockPublishedTplRepo,
		productRepo:      mockProductRepo,
	}

	ctx := context.Background()
	tplID := int64(123)

	// Return nil PO - this will cause a panic in the conversion
	mockPublishedTplRepo.EXPECT().GetByTplID(gomock.Any(), tplID).Return(nil, nil)

	assert.Panics(t, func() {
		_, _ = svc.PubedTplDetail(ctx, tplID)
	})
}
