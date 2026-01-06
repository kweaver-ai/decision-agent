package apiv3common

import (
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/capimiddleware"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/cenum"
	"github.com/gin-gonic/gin"
)

func GetPrivateRouterGroup(router *gin.RouterGroup) (group *gin.RouterGroup) {
	mws := []gin.HandlerFunc{
		capimiddleware.SetInternalAPIUserInfo(false),
		capimiddleware.SetInternalAPIFlag(),
	}

	group = router.Group("", mws...)

	return
}

// GetPrivateRouterGroupWithAccountTypes 支持指定 AccountType 参数的私有路由组
func GetPrivateRouterGroupWithAccountTypes(router *gin.RouterGroup, accountTypes ...cenum.AccountType) (group *gin.RouterGroup) {
	mws := []gin.HandlerFunc{
		capimiddleware.SetInternalAPIUserInfo(true, accountTypes...),
		capimiddleware.SetInternalAPIFlag(),
	}

	group = router.Group("", mws...)

	return
}
