package permissionhandler

import (
	"sync"

	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-factory/src/domain/service/inject/v3/dainject"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-factory/src/driveradapter/api/public/v3/apiv3common"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-factory/src/port/driver/ihandlerportdriver"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-factory/src/port/driver/iv3portdriver"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/cmp/icmp"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/cenum"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/mdl-go-lib/logger"

	"github.com/gin-gonic/gin"
)

type permissionHandler struct {
	logger        icmp.Logger
	permissionSvc iv3portdriver.IPermissionSvc
}

func (h *permissionHandler) RegPubRouter(router *gin.RouterGroup) {
	// 权限相关路由
	router.POST("/agent-permission/execute", h.CheckUsePermission)
	// router.POST("/agent-permission/is-custom-space-member", h.CheckIsCustomSpaceMember)

	router.GET("/agent-permission/management/user-status", h.GetUserStatus)
}

func (h *permissionHandler) RegPriRouter(router *gin.RouterGroup) {
	g := apiv3common.GetPrivateRouterGroupWithAccountTypes(router, cenum.AccountTypeUser, cenum.AccountTypeApp)

	// 私有路由注册
	g.POST("/agent-permission/execute", h.CheckUsePermission)
	// g.POST("/agent-permission/is-custom-space-member", h.CheckIsCustomSpaceMember)

	g.GET("/agent-permission/management/user-status", h.GetUserStatus)
}

var (
	handlerOnce sync.Once
	_handler    ihandlerportdriver.IHTTPRouter
)

func NewPermissionHandler() ihandlerportdriver.IHTTPRouter {
	handlerOnce.Do(func() {
		_handler = &permissionHandler{
			logger:        logger.GetLogger(),
			permissionSvc: dainject.NewPermissionSvc(),
		}
	})

	return _handler
}
