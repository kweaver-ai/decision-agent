package v3agentconfighandler

import (
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-factory/src/driveradapter/api/rdto/agent_config/agentconfigreq"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/capimiddleware"
	"github.com/gin-gonic/gin"
)

func setIsPrivate2Req(c *gin.Context, req *agentconfigreq.UpdateReq) {
	isPrivate := capimiddleware.IsInternalAPI(c)

	req.IsInternalAPI = isPrivate
}
