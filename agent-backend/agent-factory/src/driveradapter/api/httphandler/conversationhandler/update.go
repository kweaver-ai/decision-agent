package conversationhandler

import (
	"fmt"
	"net/http"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/conversation/conversationreq"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/capierr"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper"
	otelHelper "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry"
	"github.com/kweaver-ai/kweaver-go-lib/rest"

	"github.com/gin-gonic/gin"
	"github.com/pkg/errors"
)

func (h *conversationHTTPHandler) Update(c *gin.Context) {
	// 接收语言标识转换为 context.Context
	ctx := rest.GetLanguageCtx(c)
	// 1. 获取请求参数
	var req conversationreq.UpdateReq

	req.ID = c.Param("id")

	if err := c.ShouldBindJSON(&req); err != nil {
		h.logger.Errorf("[Update] should bind json error: %v", errors.Cause(err))
		otelHelper.Errorf(c, "[Update] should bind json error: %v", errors.Cause(err))
		err = capierr.New400Err(c, chelper.ErrMsg(err, &req))
		rest.ReplyError(c, err)

		return
	}

	// 2. 验证请求参数
	if err := req.ReqCheck(); err != nil {
		h.logger.Errorf("[Update] req check error: %v", errors.Cause(err))
		otelHelper.Errorf(c, "[Update] req check error: %v", errors.Cause(err))
		err = capierr.New400Err(c, err.Error())
		rest.ReplyError(c, err)

		return
	}

	err := h.conversationSvc.Update(ctx, req)
	if err != nil {
		h.logger.Errorf("update conversation failed cause: %v, err trace: %+v\n", errors.Cause(err), err)
		otelHelper.Errorf(c, "update conversation failed cause: %v, err trace: %+v\n", errors.Cause(err), err)
		// 返回错误
		rest.ReplyError(c, err)

		return
	}

	rest.ReplyOK(c, http.StatusNoContent, "")
}
