package publishedsvc

import (
	"context"
	"errors"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/published/pubedreq"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/ibizdomainacc/bizdomainaccmock"
	"github.com/stretchr/testify/assert"
)

// Helper function to create context with business domain ID
func createPublishedCtx(bdID string) context.Context {
	ctx := context.Background()
	ctx = context.WithValue(ctx, cenum.BizDomainIDCtxKey.String(), bdID)
	return ctx
}

func TestGetPubedTplList_BizDomainHttpError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockBizDomainHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)
	mockPublishedTplRepo := idbaccessmock.NewMockIPublishedTplRepo(ctrl)

	req := &pubedreq.PubedTplListReq{
		Size: 10,
	}

	expectedErr := errors.New("business domain error")
	mockBizDomainHttp.EXPECT().GetAllAgentTplIDList(gomock.Any(), []string{"bd-123"}).Return(nil, expectedErr)

	svc := &publishedSvc{
		SvcBase:          service.NewSvcBase(),
		bizDomainHttp:    mockBizDomainHttp,
		publishedTplRepo: mockPublishedTplRepo,
	}

	ctx := createPublishedCtx("bd-123")
	res, err := svc.GetPubedTplList(ctx, req)

	assert.Error(t, err)
	assert.NotNil(t, res)
	assert.Contains(t, err.Error(), "bizDomainHttp.GetAllAgentTplIDList failed")
}

func TestGetPubedTplList_NoTemplatesInBusinessDomain(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockBizDomainHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)
	mockPublishedTplRepo := idbaccessmock.NewMockIPublishedTplRepo(ctrl)

	req := &pubedreq.PubedTplListReq{
		Size: 10,
	}

	mockBizDomainHttp.EXPECT().GetAllAgentTplIDList(gomock.Any(), []string{"bd-123"}).Return([]string{}, nil)

	svc := &publishedSvc{
		SvcBase:          service.NewSvcBase(),
		bizDomainHttp:    mockBizDomainHttp,
		publishedTplRepo: mockPublishedTplRepo,
	}

	ctx := createPublishedCtx("bd-123")
	res, err := svc.GetPubedTplList(ctx, req)

	assert.NoError(t, err)
	assert.NotNil(t, res)
	assert.True(t, res.IsLastPage)
}

func TestGetPubedTplList_RepositoryError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockBizDomainHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)
	mockPublishedTplRepo := idbaccessmock.NewMockIPublishedTplRepo(ctrl)

	req := &pubedreq.PubedTplListReq{
		Size: 10,
	}

	tplIDs := []string{"tpl-1", "tpl-2"}
	expectedErr := errors.New("repository error")

	mockBizDomainHttp.EXPECT().GetAllAgentTplIDList(gomock.Any(), []string{"bd-123"}).Return(tplIDs, nil)
	mockPublishedTplRepo.EXPECT().GetPubTplList(gomock.Any(), req).Return(nil, expectedErr)

	svc := &publishedSvc{
		SvcBase:          service.NewSvcBase(),
		bizDomainHttp:    mockBizDomainHttp,
		publishedTplRepo: mockPublishedTplRepo,
	}

	ctx := createPublishedCtx("bd-123")
	res, err := svc.GetPubedTplList(ctx, req)

	assert.Error(t, err)
	assert.NotNil(t, res)
	assert.Contains(t, err.Error(), "publishedTplRepo.GetPubTplList failed")
}

func TestGetPubedTplList_EmptyResults(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockBizDomainHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)
	mockPublishedTplRepo := idbaccessmock.NewMockIPublishedTplRepo(ctrl)

	req := &pubedreq.PubedTplListReq{
		Size: 10,
	}

	tplIDs := []string{"tpl-1", "tpl-2"}

	mockBizDomainHttp.EXPECT().GetAllAgentTplIDList(gomock.Any(), []string{"bd-123"}).Return(tplIDs, nil)
	mockPublishedTplRepo.EXPECT().GetPubTplList(gomock.Any(), req).Return([]*dapo.PublishedTplPo{}, nil)

	svc := &publishedSvc{
		SvcBase:          service.NewSvcBase(),
		bizDomainHttp:    mockBizDomainHttp,
		publishedTplRepo: mockPublishedTplRepo,
		umHttp:           nil,
	}

	ctx := createPublishedCtx("bd-123")
	res, err := svc.GetPubedTplList(ctx, req)

	// When repo returns empty list, the function returns without error (no p2e conversion)
	assert.NoError(t, err)
	assert.NotNil(t, res)
}

func TestGetPublishedAgentList_Success(t *testing.T) {
	t.Skip("Skipping - requires multiple dependencies to be set up")
}
