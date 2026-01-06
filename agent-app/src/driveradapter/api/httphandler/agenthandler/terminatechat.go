package agenthandler

import (
	"fmt"
	"net/http"

	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/common/capierr"
	agentreq "github.com/data-agent/agent-app/src/driveradapter/api/rdto/agent/req"
	"github.com/gin-gonic/gin"
	o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
)

func (h *agentHTTPHandler) TerminateChat(c *gin.Context) {
	var req agentreq.TerminateReq
	if err := c.ShouldBindJSON(&req); err != nil {
		h.logger.Errorf("[TerminateChat] should bind json error: %v", err)
		o11y.Error(c, fmt.Sprintf("[TerminateChat] should bind json error: %v", err))
		rest.ReplyError(c, err)

		return
	}

	if req.ConversationID == "" {
		h.logger.Errorf("[TerminateChat] conversation_id is required")
		o11y.Error(c, "[TerminateChat] conversation_id is required")
		rest.ReplyError(c, capierr.New400Err(c, "conversation_id is required"))

		return
	}

	err := h.agentSvc.TerminateChat(c.Request.Context(), req.ConversationID)
	if err != nil {
		h.logger.Errorf("[TerminateChat] terminate chat error: %v", err)
		o11y.Error(c, fmt.Sprintf("[TerminateChat] terminate chat error: %v", err))
		rest.ReplyError(c, err)

		return
	}

	rest.ReplyOK(c, http.StatusNoContent, nil)
}
