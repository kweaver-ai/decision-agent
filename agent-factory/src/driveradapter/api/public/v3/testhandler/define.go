package testhandler

import (
	"sync"

	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-factory/src/driveradapter/api/public/v3/apiv3common"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-factory/src/driveradapter/api/public/v3/testhandler/bizdomain"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-factory/src/port/driver/ihandlerportdriver"
	"github.com/gin-gonic/gin"
)

type testHTTPHandler struct {
	bizDomainHandler *bizdomain.BizDomainTestHandler
}

func (t *testHTTPHandler) RegPubRouter(router *gin.RouterGroup) {
}

func (t *testHTTPHandler) RegPriRouter(router *gin.RouterGroup) {
	g := apiv3common.GetPrivateRouterGroup(router)

	// 私有路由注册
	// 委托给bizdomain handler注册路由
	t.bizDomainHandler.RegisterRoutes(g)
}

var (
	handlerOnce sync.Once
	_handler    ihandlerportdriver.IHTTPRouter
)

func NewTestHTTPHandler() ihandlerportdriver.IHTTPRouter {
	handlerOnce.Do(func() {
		_handler = &testHTTPHandler{
			bizDomainHandler: bizdomain.NewBizDomainTestHandler(),
		}
	})

	return _handler
}
