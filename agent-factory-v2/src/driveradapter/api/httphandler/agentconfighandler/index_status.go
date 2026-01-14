package v3agentconfighandler

import (
	"net/http"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent_config/agentconfigreq"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/common"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/capierr"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/gin-gonic/gin"
)

func (h *daConfHTTPHandler) BatchCheckIndexStatus(c *gin.Context) {
	// 1. 获取请求参数
	var req agentconfigreq.BatchCheckIndexStatusReq

	if err := c.ShouldBindJSON(&req); err != nil {
		err = capierr.New400Err(c, chelper.ErrMsg(err, &req))
		rest.ReplyError(c, err)

		return
	}

	// 2. 验证请求参数
	if err := req.ReqCheck(); err != nil {
		err = capierr.New400Err(c, err.Error())
		rest.ReplyError(c, err)

		return
	}

	// 3. 批量检查索引状态
	res, err := h.daConfSvc.BatchCheckIndexStatus(c, &req)
	if err != nil {
		rest.ReplyError(c, err)
		return
	}

	list := common.NewListCommon()
	list.SetEntries(res)

	// 4. 返回结果
	c.JSON(http.StatusOK, list)
}
