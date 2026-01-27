package agenthandler

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
	agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/capierr"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	otelHelper "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry"
)

func (h *agentHTTPHandler) TerminateChat(c *gin.Context) {
	var req agentreq.TerminateReq
	if err := c.ShouldBindJSON(&req); err != nil {
		h.logger.Errorf("[TerminateChat] should bind json error: %v", err)
		otelHelper.Errorf(c, "[TerminateChat] should bind json error: %v", err)
		rest.ReplyError(c, err)

		return
	}

	if req.ConversationID == "" {
		h.logger.Errorf("[TerminateChat] conversation_id is required")
		otelHelper.Error(c, "[TerminateChat] conversation_id is required")
		rest.ReplyError(c, capierr.New400Err(c, "conversation_id is required"))

		return
	}

	err := h.agentSvc.TerminateChat(c.Request.Context(), req.ConversationID, req.AgentRunID)
	if err != nil {
		h.logger.Errorf("[TerminateChat] terminate chat error: %v", err)
		otelHelper.Errorf(c, "[TerminateChat] terminate chat error: %v", err)
		rest.ReplyError(c, err)

		return
	}

	rest.ReplyOK(c, http.StatusNoContent, nil)
}
