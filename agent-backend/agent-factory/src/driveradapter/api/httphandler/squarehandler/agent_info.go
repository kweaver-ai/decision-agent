package squarehandler

import (
	"net/http"

	"github.com/pkg/errors"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/square/squarereq"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/capierr"

	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/gin-gonic/gin"
)

func (h *squareHandler) AgentInfo(c *gin.Context) {
	// 接收语言标识转换为 context.Context
	ctx := rest.GetLanguageCtx(c)

	// 1. get req
	iReq, exists := c.Get(agentInfoReqCtxKey)
	if !exists {
		err := capierr.New400Err(c, "[AgentInfo]: agentInfoReqCtxKey不存在")
		_ = c.Error(err)
		c.Abort()

		return
	}

	req, ok := iReq.(*squarereq.AgentInfoReq)
	if !ok {
		err := capierr.New400Err(c, "[AgentInfo]: agentInfoReqCtxKey类型错误")
		_ = c.Error(err)
		c.Abort()

		return
	}

	// 2. 获取 agent 信息
	agentInfo, err := h.squareSvc.GetAgentInfo(ctx, req)
	if err != nil {
		h.logger.Errorf("GetPublishAgentList error cause: %v, err trace: %+v\n", errors.Cause(err), err)

		_ = c.Error(err)

		return
	}

	// 3. 返回成功
	rest.ReplyOK(c, http.StatusOK, agentInfo)
}
