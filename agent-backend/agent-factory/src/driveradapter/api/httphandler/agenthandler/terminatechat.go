package agenthandler

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
	agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/capierr"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/otel/otellog"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/otel/oteltrace"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
)

func (h *agentHTTPHandler) TerminateChat(c *gin.Context) {
	var req agentreq.TerminateReq
	if err := c.ShouldBindJSON(&req); err != nil {
		h.logger.Errorf("[TerminateChat] should bind json error: %v", err)
		otellog.LogError(c, fmt.Sprintf("[TerminateChat] should bind json error: %v", err), err)
		rest.ReplyError(c, err)

		return
	}

	oteltrace.SetConversationID(c.Request.Context(), req.ConversationID)

	if req.ConversationID == "" {
		h.logger.Errorf("[TerminateChat] conversation_id is required")
		otellog.LogError(c, "[TerminateChat] conversation_id is required", nil)
		rest.ReplyError(c, capierr.New400Err(c, "conversation_id is required"))

		return
	}

	err := h.agentSvc.TerminateChat(c.Request.Context(), req.ConversationID, req.AgentRunID, req.InterruptedAssistantMessageID)
	if err != nil {
		h.logger.Errorf("[TerminateChat] terminate chat error: %v", err)
		otellog.LogError(c, fmt.Sprintf("[TerminateChat] terminate chat error: %v", err), err)
		rest.ReplyError(c, err)

		return
	}

	rest.ReplyOK(c, http.StatusNoContent, nil)
}
