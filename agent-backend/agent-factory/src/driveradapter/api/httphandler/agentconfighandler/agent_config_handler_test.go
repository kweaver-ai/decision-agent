package v3agentconfighandler

import (
	"context"
	"errors"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/gin-gonic/gin/binding"
	"github.com/go-playground/validator/v10"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"go.uber.org/mock/gomock"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/auditlogdto"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent_config/agentconfigresp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/customvalidator"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driver/iv3portdriver/v3portdrivermock"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
)

type acTestLogger struct{}

func (acTestLogger) Infof(string, ...interface{})  {}
func (acTestLogger) Infoln(...interface{})         {}
func (acTestLogger) Debugf(string, ...interface{}) {}
func (acTestLogger) Debugln(...interface{})        {}
func (acTestLogger) Errorf(string, ...interface{}) {}
func (acTestLogger) Errorln(...interface{})        {}
func (acTestLogger) Warnf(string, ...interface{})  {}
func (acTestLogger) Warnln(...interface{})         {}
func (acTestLogger) Panicf(string, ...interface{}) {}
func (acTestLogger) Panicln(...interface{})        {}
func (acTestLogger) Fatalf(string, ...interface{}) {}
func (acTestLogger) Fatalln(...interface{})        {}

func newACTestCtx(method, target, body string) (*gin.Context, *httptest.ResponseRecorder) {
	gin.SetMode(gin.TestMode)

	recorder := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(recorder)

	req := httptest.NewRequest(method, target, strings.NewReader(body))
	if body != "" {
		req.Header.Set("Content-Type", "application/json")
	}

	c.Request = req

	return c, recorder
}

func setACInternalAPI(c *gin.Context) {
	c.Set(cenum.InternalAPIFlagCtxKey.String(), true)
	ctx := context.WithValue(c.Request.Context(), cenum.InternalAPIFlagCtxKey.String(), true)
	c.Request = c.Request.WithContext(ctx)
}

func setACVisitor(c *gin.Context, userID string) {
	visitor := &rest.Visitor{ID: userID}
	c.Set(cenum.VisitUserInfoCtxKey.String(), visitor)
}

func registerACValidators(t *testing.T) {
	t.Helper()

	v, ok := binding.Validator.Engine().(*validator.Validate)
	require.True(t, ok)

	_ = v.RegisterValidation("checkAgentAndTplName", customvalidator.CheckAgentAndTplName)
}

func hasRoute(routes gin.RoutesInfo, method, path string) bool {
	for _, r := range routes {
		if r.Method == method && r.Path == path {
			return true
		}
	}

	return false
}

// --- Route Registration Tests ---

func TestDAConfHTTPHandler_RegPubRouter(t *testing.T) {
	t.Parallel()

	h := &daConfHTTPHandler{}
	r := gin.New()
	h.RegPubRouter(r.Group("/v3"))
	routes := r.Routes()

	assert.True(t, hasRoute(routes, http.MethodPost, "/v3/agent"))
	assert.True(t, hasRoute(routes, http.MethodPut, "/v3/agent/:agent_id"))
	assert.True(t, hasRoute(routes, http.MethodGet, "/v3/agent/:agent_id"))
	assert.True(t, hasRoute(routes, http.MethodGet, "/v3/agent/by-key/:key"))
	assert.True(t, hasRoute(routes, http.MethodDelete, "/v3/agent/:agent_id"))
	assert.True(t, hasRoute(routes, http.MethodPost, "/v3/agent/ai-autogen"))
	assert.True(t, hasRoute(routes, http.MethodGet, "/v3/agent/avatar/built-in"))
}

func TestDAConfHTTPHandler_RegPriRouter(t *testing.T) {
	t.Parallel()

	h := &daConfHTTPHandler{}
	r := gin.New()
	h.RegPriRouter(r.Group("/internal"))
	routes := r.Routes()

	assert.NotEmpty(t, routes)
}

// --- Detail handler tests ---

func TestDAConfHTTPHandler_Detail_EmptyID(t *testing.T) {
	t.Parallel()

	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockSvc := v3portdrivermock.NewMockIDataAgentConfigSvc(ctrl)
	h := &daConfHTTPHandler{daConfSvc: mockSvc, logger: acTestLogger{}}

	c, recorder := newACTestCtx(http.MethodGet, "/v3/agent/", "")
	c.Params = gin.Params{{Key: "agent_id", Value: ""}}

	h.Detail(c)

	assert.Equal(t, http.StatusBadRequest, recorder.Code)
}

func TestDAConfHTTPHandler_Detail_ServiceError(t *testing.T) {
	t.Parallel()

	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockSvc := v3portdrivermock.NewMockIDataAgentConfigSvc(ctrl)
	mockSvc.EXPECT().Detail(gomock.Any(), "agent-1", "").Return(nil, errors.New("not found"))

	h := &daConfHTTPHandler{daConfSvc: mockSvc, logger: acTestLogger{}}

	c, recorder := newACTestCtx(http.MethodGet, "/v3/agent/agent-1", "")
	c.Params = gin.Params{{Key: "agent_id", Value: "agent-1"}}

	h.Detail(c)

	assert.NotEqual(t, http.StatusOK, recorder.Code)
}

func TestDAConfHTTPHandler_Detail_Happy(t *testing.T) {
	t.Parallel()

	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockSvc := v3portdrivermock.NewMockIDataAgentConfigSvc(ctrl)
	mockSvc.EXPECT().Detail(gomock.Any(), "agent-1", "").Return(&agentconfigresp.DetailRes{}, nil)

	h := &daConfHTTPHandler{daConfSvc: mockSvc, logger: acTestLogger{}}

	c, recorder := newACTestCtx(http.MethodGet, "/v3/agent/agent-1", "")
	c.Params = gin.Params{{Key: "agent_id", Value: "agent-1"}}

	h.Detail(c)

	assert.Equal(t, http.StatusOK, recorder.Code)
}

// --- DetailByKey handler tests ---

func TestDAConfHTTPHandler_DetailByKey_EmptyKey(t *testing.T) {
	t.Parallel()

	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockSvc := v3portdrivermock.NewMockIDataAgentConfigSvc(ctrl)
	h := &daConfHTTPHandler{daConfSvc: mockSvc, logger: acTestLogger{}}

	c, recorder := newACTestCtx(http.MethodGet, "/v3/agent/by-key/", "")
	c.Params = gin.Params{{Key: "key", Value: ""}}

	h.DetailByKey(c)

	assert.Equal(t, http.StatusBadRequest, recorder.Code)
}

func TestDAConfHTTPHandler_DetailByKey_Happy(t *testing.T) {
	t.Parallel()

	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockSvc := v3portdrivermock.NewMockIDataAgentConfigSvc(ctrl)
	mockSvc.EXPECT().Detail(gomock.Any(), "", "my-key").Return(&agentconfigresp.DetailRes{}, nil)

	h := &daConfHTTPHandler{daConfSvc: mockSvc, logger: acTestLogger{}}

	c, recorder := newACTestCtx(http.MethodGet, "/v3/agent/by-key/my-key", "")
	c.Params = gin.Params{{Key: "key", Value: "my-key"}}

	h.DetailByKey(c)

	assert.Equal(t, http.StatusOK, recorder.Code)
}

// --- Create handler tests ---

func TestDAConfHTTPHandler_Create_BadJSON(t *testing.T) {
	t.Parallel()

	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockSvc := v3portdrivermock.NewMockIDataAgentConfigSvc(ctrl)
	h := &daConfHTTPHandler{daConfSvc: mockSvc, logger: acTestLogger{}}

	c, _ := newACTestCtx(http.MethodPost, "/v3/agent", "not-json")
	setACInternalAPI(c)

	h.Create(c)
	assert.NotEmpty(t, c.Errors)
}

func TestDAConfHTTPHandler_Create_BadJSONMissingRequired(t *testing.T) {
	t.Parallel()

	registerACValidators(t)

	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockSvc := v3portdrivermock.NewMockIDataAgentConfigSvc(ctrl)
	h := &daConfHTTPHandler{daConfSvc: mockSvc, logger: acTestLogger{}}

	body := `{"name":"test-agent"}`
	c, _ := newACTestCtx(http.MethodPost, "/v3/agent", body)
	setACInternalAPI(c)

	h.Create(c)
	assert.NotEmpty(t, c.Errors)
}

// --- Delete handler tests ---

func TestDAConfHTTPHandler_Delete_Happy(t *testing.T) {
	t.Parallel()

	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockSvc := v3portdrivermock.NewMockIDataAgentConfigSvc(ctrl)
	mockSvc.EXPECT().Delete(gomock.Any(), "agent-1", gomock.Any(), gomock.Any()).
		Return(auditlogdto.AgentDeleteAuditLogInfo{}, nil)

	h := &daConfHTTPHandler{daConfSvc: mockSvc, logger: acTestLogger{}}

	c, recorder := newACTestCtx(http.MethodDelete, "/v3/agent/agent-1", "")
	c.Params = gin.Params{{Key: "agent_id", Value: "agent-1"}}
	setACInternalAPI(c)
	c.Set(cenum.VisitUserIDCtxKey.String(), "user-1")

	h.Delete(c)

	assert.NotEqual(t, http.StatusInternalServerError, recorder.Code)
}
