package agenthandler

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
	agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/apierr"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	otelHelper "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry"
	"github.com/pkg/errors"
)

func (h *agentHTTPHandler) FileCheck(c *gin.Context) {
	// 1. 获取请求参数
	var req agentreq.FileCheckReq
	if err := c.ShouldBindJSON(&req); err != nil {
		h.logger.Errorf("FileCheck error cause: %v, err trace: %+v\n", errors.Cause(err), err)
		httpErr := rest.NewHTTPError(c.Request.Context(), http.StatusBadRequest, apierr.AgentAPP_InvalidParameter_RequestBody).WithErrorDetails(err.Error())
		o11y.Error(c.Request.Context(), fmt.Sprintf("[FileCheck] error cause: %v, err trace: %+v\n", errors.Cause(err), err))
		rest.ReplyError(c, httpErr)

		return
	}

	// 2. 调用服务
	rsp, err := h.agentSvc.FileCheck(c.Request.Context(), &req)
	if err != nil {
		h.logger.Errorf("FileCheck error cause: %v, err trace: %+v\n", errors.Cause(err), err)
		o11y.Error(c.Request.Context(), fmt.Sprintf("[FileCheck] error cause: %v, err trace: %+v\n", errors.Cause(err), err))
		httpErr := rest.NewHTTPError(c.Request.Context(), http.StatusInternalServerError, apierr.AgentAPP_InternalError).WithErrorDetails(err.Error())
		rest.ReplyError(c, httpErr)

		return
	}

	// 3. 返回响应
	rest.ReplyOK(c, http.StatusOK, rsp)
}
