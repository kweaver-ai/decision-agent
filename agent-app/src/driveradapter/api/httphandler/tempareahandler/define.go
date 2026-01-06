package tempareahandler

import (
	"sync"

	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/cmp/icmp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/common/capimiddleware"
	"github.com/data-agent/agent-app/src/domain/service/inject/dainject"
	"github.com/data-agent/agent-app/src/port/driver/ihandlerportdriver"
	"github.com/data-agent/agent-app/src/port/driver/iportdriver"
	"github.com/kweaver-ai/kweaver-go-lib/logger"

	"github.com/gin-gonic/gin"
)

type tempareaHTTPHandler struct {
	tempareaSvc iportdriver.ITempAreaSvc
	logger      icmp.Logger
}

func (h *tempareaHTTPHandler) RegPubRouter(router *gin.RouterGroup) {
	router.POST("/temparea", h.Create)
	router.PUT("/temparea/:id", h.Append)
	router.DELETE("/temparea/:id", h.Remove)
	router.GET("/temparea/:id", h.Get)
}

func (h *tempareaHTTPHandler) RegPriRouter(router *gin.RouterGroup) {
	router.Use(capimiddleware.SetInternalAPIFlag())
}

var (
	handlerOnce sync.Once
	_handler    ihandlerportdriver.IHTTPRouter
)

func NewTempareaHTTPHandler() ihandlerportdriver.IHTTPRouter {
	handlerOnce.Do(func() {
		_handler = &tempareaHTTPHandler{
			tempareaSvc: dainject.NewTempAreaSvc(),
			logger:      logger.GetLogger(),
		}
	})

	return _handler
}
