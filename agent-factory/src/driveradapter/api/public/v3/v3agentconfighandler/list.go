package v3agentconfighandler

import (
	"net/http"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent_config/agentconfigreq"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/capierr"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/gin-gonic/gin"
	"github.com/pkg/errors"
)

func (h *daConfHTTPHandler) AgentListListForBenchmark(c *gin.Context) {
	// 接收语言标识转换为 context.Context
	ctx := rest.GetLanguageCtx(c)
	req := &agentconfigreq.ListForBenchmarkReq{}

	if err := c.ShouldBindQuery(req); err != nil {
		httpErr := capierr.New400Err(c, chelper.ErrMsg(err, req))
		_ = c.Error(httpErr)

		return
	}

	resp, err := h.daConfSvc.ListForBenchmark(ctx, req)
	if err != nil {
		h.logger.Errorf("AgentList error cause: %v, err trace: %+v\n", errors.Cause(err), err)

		_ = c.Error(err)

		return
	}

	// 返回成功
	rest.ReplyOK(c, http.StatusOK, resp)
}
