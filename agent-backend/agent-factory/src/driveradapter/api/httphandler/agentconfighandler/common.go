package v3agentconfighandler

import (
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent_config/agentconfigreq"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/capimiddleware"
	"github.com/gin-gonic/gin"
)

func setIsPrivate2Req(c *gin.Context, req *agentconfigreq.UpdateReq) {
	isPrivate := capimiddleware.IsInternalAPI(c)

	req.IsInternalAPI = isPrivate
}
