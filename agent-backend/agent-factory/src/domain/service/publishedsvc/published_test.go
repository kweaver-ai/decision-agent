package publishedsvc

import (
	"context"
	"errors"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	pubedreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/published/pubedreq"
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

	dto := &NewPublishedSvcDto{
		SvcBase:          service.NewSvcBase(),
		PublishedTplRepo: mockPublishedTplRepo,
		BizDomainHttp:    mockBizDomainHttp,
	}

	svc := NewPublishedService(dto)

	ctx := createPublishedCtx("test-bd-id")
	req := &pubedreq.PubedTplListReq{
		Size: 10,
	}

	httpErr := errors.New("http request failed")

	mockBizDomainHttp.EXPECT().GetAllAgentTplIDList(gomock.Any(), gomock.Any()).Return(nil, httpErr)

	res, err := svc.GetPubedTplList(ctx, req)

	// The function returns both response and error
	assert.Error(t, err)
	assert.NotNil(t, res) // Response is initialized even on error
	assert.Contains(t, err.Error(), "bizDomainHttp.GetAllAgentTplIDList failed")
}

func TestGetPubedTplList_NoTemplatesInBusinessDomain(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockBizDomainHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)
	mockPublishedTplRepo := idbaccessmock.NewMockIPublishedTplRepo(ctrl)

	dto := &NewPublishedSvcDto{
		SvcBase:          service.NewSvcBase(),
		PublishedTplRepo: mockPublishedTplRepo,
		BizDomainHttp:    mockBizDomainHttp,
	}

	svc := NewPublishedService(dto)

	ctx := createPublishedCtx("test-bd-id")
	req := &pubedreq.PubedTplListReq{
		Size: 10,
	}

	// When GetAllAgentTplIDList returns empty, the function returns early without calling the repo
	mockBizDomainHttp.EXPECT().GetAllAgentTplIDList(gomock.Any(), gomock.Any()).Return([]string{}, nil)

	res, err := svc.GetPubedTplList(ctx, req)

	assert.NoError(t, err)
	assert.NotNil(t, res)
	assert.True(t, res.IsLastPage)
}

func TestGetPubedTplList_TemplatesInBusinessDomain(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockBizDomainHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)
	mockPublishedTplRepo := idbaccessmock.NewMockIPublishedTplRepo(ctrl)

	dto := &NewPublishedSvcDto{
		SvcBase:          service.NewSvcBase(),
		PublishedTplRepo: mockPublishedTplRepo,
		BizDomainHttp:    mockBizDomainHttp,
	}

	ctx := createPublishedCtx("test-bd-id")
	req := &pubedreq.PubedTplListReq{
		Size: 10,
	}

	// Mock HTTP to return template IDs
	mockBizDomainHttp.EXPECT().GetAllAgentTplIDList(gomock.Any(), gomock.Any()).Return([]string{"tpl1", "tpl2"}, nil)

	// Mock repository to return templates
	mockTemplates := []*dapo.PublishedTplPo{
		{TplID: 1, BizDomainID: "test-bd-id", Name: "Template 1"},
		{TplID: 2, BizDomainID: "test-bd-id", Name: "Template 2"},
	}
	mockPublishedTplRepo.EXPECT().GetPubTplList(gomock.Any(), gomock.Any()).Return(mockTemplates, nil)

	res, err := svc.GetPubedTplList(ctx, req)

	assert.NoError(t, err)
	assert.NotNil(t, res)
	assert.False(t, res.IsLastPage) // Has more results
	assert.NotEmpty(t, res.PublishedAgentTplList)
}

func TestGetPubedTplList_PartialPage(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockBizDomainHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)
	mockPublishedTplRepo := idbaccessmock.NewMockIPublishedTplRepo(ctrl)

	dto := &NewPublishedSvcDto{
		SvcBase:          service.NewSvcBase(),
		PublishedTplRepo: mockPublishedTplRepo,
		BizDomainHttp:    mockBizDomainHttp,
	}

	ctx := createPublishedCtx("test-bd-id")
	req := &pubedreq.PubedTplListReq{
		Size: 1, // Only get 1 template
	}

	// Mock HTTP to return more templates than requested
	mockBizDomainHttp.EXPECT().GetAllAgentTplIDList(gomock.Any(), gomock.Any()).Return([]string{"tpl1", "tpl2"}, nil)

	// Mock repository to return only 1 template
	mockTemplates := []*dapo.PublishedTplPo{
		{TplID: 1, BizDomainID: "test-bd-id", Name: "Template 1"},
	}
	mockPublishedTplRepo.EXPECT().GetPubTplList(gomock.Any(), gomock.Any()).Return(mockTemplates, nil)

	res, err := svc.GetPubedTplList(ctx, req)

	assert.NoError(t, err)
	assert.NotNil(t, res)
	assert.True(t, res.IsLastPage) // Only 1 result but requested size 1
	assert.NotEmpty(t, res.PublishedAgentTplList)
}

func TestGetPubedTplList_PaginationWithMorePages(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockBizDomainHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)
	mockPublishedTplRepo := idbaccessmock.NewMockIPublishedTplRepo(ctrl)

	dto := &NewPublishedSvcDto{
		SvcBase:          service.NewSvcBase(),
		PublishedTplRepo: mockPublishedTplRepo,
		BizDomainHttp:    mockBizDomainHttp,
	}

	ctx := createPublishedCtx("test-bd-id")
	req := &pubedreq.PubedTplListReq{
		Size: 1,
	}

	// Mock HTTP to return 1 template (simulating second page being empty)
	mockBizDomainHttp.EXPECT().GetAllAgentTplIDList(gomock.Any(), gomock.Any()).Return([]string{"tpl1"}, nil)
	mockPublishedTplRepo.EXPECT().GetPubTplList(gomock.Any(), gomock.Any()).Return([]*dapo.PublishedTplPo{}, nil)

	res, err := svc.GetPubedTplList(ctx, req)

	assert.NoError(t, err)
	assert.NotNil(t, res)
	assert.True(t, res.IsLastPage) // No more templates after first page
	assert.Empty(t, res.PublishedAgentTplList)
}

func TestGetPubedTplList_WithOffset(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockBizDomainHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)
	mockPublishedTplRepo := idbaccessmock.NewMockIPublishedTplRepo(ctrl)

	dto := &NewPublishedSvcDto{
		SvcBase:          service.NewSvcBase(),
		PublishedTplRepo: mockPublishedTplRepo,
		BizDomainHttp:    mockBizDomainHttp,
	}

	ctx := createPublishedCtx("test-bd-id")
	req := &pubedreq.PubedTplListReq{
		Size: 10,
	}

	// Mock to return templates starting from offset
	mockTemplates := []*dapo.PublishedTplPo{
		{TplID: 3, BizDomainID: "test-bd-id", Name: "Template 3"},
		{TplID: 4, BizDomainID: "test-bd-id", Name: "Template 4"},
	}
	mockPublishedTplRepo.EXPECT().GetPubTplList(gomock.Any(), gomock.Any()).Return(mockTemplates, nil)

	res, err := svc.GetPubedTplList(ctx, req)

	assert.NoError(t, err)
	assert.NotNil(t, res)
	assert.False(t, res.IsLastPage)
	assert.NotEmpty(t, res.PublishedAgentTplList)
}

func TestGetPubedTplList_ConvertToEosError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockBizDomainHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)
	mockPublishedTplRepo := idbaccessmock.NewMockIPublishedTplRepo(ctrl)

	dto := &NewPublishedSvcDto{
		SvcBase:          service.NewSvcBase(),
		PublishedTplRepo: mockPublishedTplRepo,
		BizDomainHttp:    mockBizDomainHttp,
	}

	ctx := createPublishedCtx("test-bd-id")
	req := &pubedreq.PubedTplListReq{
		Size: 10,
	}

	eosErr := errors.New("convert to eos failed")

	// Mock convert to eos to fail
	mockBizDomainHttp.EXPECT().GetAllAgentTplIDList(gomock.Any(), gomock.Any()).Return([]string{"tpl1"}, nil)

	res, err := svc.GetPubedTplList(ctx, req)

	assert.Error(t, err)
	assert.NotNil(t, res) // Response is still created on error
	assert.Contains(t, err.Error(), "convert published agent template list failed")
}

func TestGetPubedTplList_RepoError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockBizDomainHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)
	mockPublishedTplRepo := idbaccessmock.NewMockIPublishedTplRepo(ctrl)

	dto := &NewPublishedSvcDto{
		SvcBase:          service.NewSvcBase(),
		PublishedTplRepo: mockPublishedTplRepo,
		BizDomainHttp:    mockBizDomainHttp,
	}

	ctx := createPublishedCtx("test-bd-id")
	req := &pubedreq.PubedTplListReq{
		Size: 10,
	}

	// Mock HTTP to return template IDs
	mockBizDomainHttp.EXPECT().GetAllAgentTplIDList(gomock.Any(), gomock.Any()).Return([]string{"tpl1"}, nil)

	// Mock repository to fail
	repoErr := errors.New("repository query failed")
	mockPublishedTplRepo.EXPECT().GetPubTplList(gomock.Any(), gomock.Any()).Return(nil, repoErr)

	res, err := svc.GetPubedTplList(ctx, req)

	assert.Error(t, err)
	assert.NotNil(t, res)
	assert.Contains(t, err.Error(), "publishedTplRepo.GetPubTplList failed")
}


func TestGetPubedTplList_RepositoryError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockBizDomainHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)
	mockPublishedTplRepo := idbaccessmock.NewMockIPublishedTplRepo(ctrl)

	dto := &NewPublishedSvcDto{
		SvcBase:          service.NewSvcBase(),
		PublishedTplRepo: mockPublishedTplRepo,
		BizDomainHttp:    mockBizDomainHttp,
	}

	svc := NewPublishedService(dto)

	ctx := createPublishedCtx("test-bd-id")
	req := &pubedreq.PubedTplListReq{
		Size: 10,
	}

	mockBizDomainHttp.EXPECT().GetAllAgentTplIDList(gomock.Any(), gomock.Any()).Return([]string{"tpl1"}, nil)
	mockPublishedTplRepo.EXPECT().GetPubTplList(gomock.Any(), gomock.Any()).Return(nil, errors.New("repository error"))

	res, err := svc.GetPubedTplList(ctx, req)

	// The function returns both response and error
	assert.Error(t, err)
	assert.NotNil(t, res) // Response is initialized even on error
	assert.Contains(t, err.Error(), "publishedTplRepo.GetPubTplList failed")
}

func TestGetPubedTplList_EmptyResults(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockBizDomainHttp := bizdomainaccmock.NewMockBizDomainHttpAcc(ctrl)
	mockPublishedTplRepo := idbaccessmock.NewMockIPublishedTplRepo(ctrl)

	dto := &NewPublishedSvcDto{
		SvcBase:          service.NewSvcBase(),
		PublishedTplRepo: mockPublishedTplRepo,
		BizDomainHttp:    mockBizDomainHttp,
	}

	svc := NewPublishedService(dto)

	ctx := createPublishedCtx("test-bd-id")
	req := &pubedreq.PubedTplListReq{
		Size: 10,
	}

	mockBizDomainHttp.EXPECT().GetAllAgentTplIDList(gomock.Any(), gomock.Any()).Return([]string{"tpl1"}, nil)
	mockPublishedTplRepo.EXPECT().GetPubTplList(gomock.Any(), gomock.Any()).Return([]*dapo.PublishedTplPo{}, nil)

	res, err := svc.GetPubedTplList(ctx, req)

	// When repo returns empty list, function returns without error (no p2e conversion)
	assert.NoError(t, err)
	assert.NotNil(t, res)
}
