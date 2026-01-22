package releasehandler

import (
	"net/http"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/constant/auditconstant"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/capierr"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/capimiddleware"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper"

	"github.com/kweaver-ai/kweaver-go-lib/audit"
	"github.com/kweaver-ai/kweaver-go-lib/rest"

	"github.com/gin-gonic/gin"
	"github.com/pkg/errors"
)

func (h *releaseHandler) UnPublish(c *gin.Context) {
	isPrivate := capimiddleware.IsInternalAPI(c)

	var visitor *rest.Visitor

	if !isPrivate {
		visitor = chelper.GetVisitorFromCtx(c.Request.Context())
	}
	// 接收语言标识转换为 context.Context
	ctx := rest.GetLanguageCtx(c)

	agentID := c.Param("agent_id")

	if agentID == "" {
		err := errors.New("agent id is empty")

		httpErr := capierr.New400Err(c, err.Error())
		if !isPrivate {
			audit.NewWarnLogWithError(audit.OPERATION, auditconstant.UNPUBLISH, audit.TransforOperator(*visitor),
				auditconstant.GenerateAgentAuditObject("", ""), &httpErr.BaseError)
		}

		_ = c.Error(httpErr)

		return
	}

	// todo validate param
	auditloginfo, err := h.releaseSvc.UnPublish(ctx, agentID)
	if err != nil {
		httpErr := capierr.New500Err(c, err.Error())
		if !isPrivate {
			audit.NewWarnLogWithError(audit.OPERATION, auditconstant.UNPUBLISH, audit.TransforOperator(*visitor),
				auditconstant.GenerateAgentAuditObject(auditloginfo.ID, auditloginfo.Name), &httpErr.BaseError)
		}

		_ = c.Error(err)

		return
	}

	if !isPrivate {
		audit.NewInfoLog(audit.OPERATION, auditconstant.UNPUBLISH, audit.TransforOperator(*visitor),
			auditconstant.GenerateAgentAuditObject(auditloginfo.ID, auditloginfo.Name), "")
	}

	rest.ReplyOK(c, http.StatusNoContent, "")
}
