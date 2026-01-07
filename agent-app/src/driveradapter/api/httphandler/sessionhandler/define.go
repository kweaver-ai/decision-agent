package sessionhandler

import (
	"sync"

	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/domain/service/inject/dainject"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driver/ihandlerportdriver"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driver/iportdriver"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/cmp/icmp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/common/capimiddleware"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/mdl-go-lib/logger"

	"github.com/gin-gonic/gin"
)

type sessionHTTPHandler struct {
	sessionSvc iportdriver.ISessionSvc
	logger     icmp.Logger
}

func (h *sessionHTTPHandler) RegPubRouter(router *gin.RouterGroup) {
	router.PUT("/conversation/session/:conversation_id", h.Manage) // 管理对话session
}

func (h *sessionHTTPHandler) RegPriRouter(router *gin.RouterGroup) {
	router.Use(capimiddleware.SetInternalAPIFlag())
}

var (
	handlerOnce sync.Once
	_handler    ihandlerportdriver.IHTTPRouter
)

func NewSessionHTTPHandler() ihandlerportdriver.IHTTPRouter {
	handlerOnce.Do(func() {
		_handler = &sessionHTTPHandler{
			sessionSvc: dainject.NewSessionSvc(),
			logger:     logger.GetLogger(),
		}
	})

	return _handler
}
