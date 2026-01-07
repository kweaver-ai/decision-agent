package v3agentconfighandler

import (
	"net/http"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/constant/auditconstant"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/apierr"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/capierr"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/capimiddleware"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper"
	"github.com/kweaver-ai/kweaver-go-lib/audit"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/gin-gonic/gin"
)

func (h *daConfHTTPHandler) Delete(c *gin.Context) {
	// 判断是否是私有API
	isPrivate := capimiddleware.IsInternalAPI(c)

	var visitor *rest.Visitor

	if !isPrivate {
		visitor = chelper.GetVisitorFromCtx(c.Request.Context())
	}
	// 1. 获取id
	id := c.Param("agent_id")
	if id == "" {
		err := capierr.New400Err(c, "id is empty")
		if !isPrivate {
			audit.NewWarnLogWithError(audit.OPERATION, auditconstant.DELETE, audit.TransforOperator(*visitor),
				auditconstant.GenerateAgentAuditObject(id, ""), &err.BaseError)
		}

		rest.ReplyError(c, err)

		return
	}

	// 2. 获取ownerUid
	uid := chelper.GetUserIDFromCtx(c)
	if !isPrivate && uid == "" {
		err := capierr.New400Err(c, "uid is empty")
		if !isPrivate {
			audit.NewWarnLogWithError(audit.OPERATION, auditconstant.DELETE, audit.TransforOperator(*visitor),
				auditconstant.GenerateAgentAuditObject(id, ""), &err.BaseError)
		}

		rest.ReplyError(c, err)

		return
	}

	// 3. 删除
	auditLogInfo, err := h.daConfSvc.Delete(c, id, uid, isPrivate)
	if err != nil {
		httpErr := rest.NewHTTPError(c, http.StatusInternalServerError, apierr.AgentFactory_InternalError).WithErrorDetails(err.Error())
		if !isPrivate {
			audit.NewWarnLogWithError(audit.OPERATION, auditconstant.DELETE, audit.TransforOperator(*visitor),
				auditconstant.GenerateAgentAuditObject(id, auditLogInfo.Name), &httpErr.BaseError)
		}

		_ = c.Error(err)

		return
	}

	if !isPrivate {
		audit.NewWarnLog(audit.OPERATION, auditconstant.DELETE, audit.TransforOperator(*visitor),
			auditconstant.GenerateAgentAuditObject(id, auditLogInfo.Name), audit.SUCCESS, "")
	}

	// 3. 返回结果
	c.Status(http.StatusNoContent)
}
