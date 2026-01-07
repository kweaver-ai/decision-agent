package agenthandler

import (
	"fmt"
	"net/http"
	"strings"

	"github.com/kweaver-ai/decision-agent/agent-app/src/domain/constant"
	"github.com/kweaver-ai/decision-agent/agent-app/src/domain/service/agentsvc"
	agentreq "github.com/kweaver-ai/decision-agent/agent-app/src/driveradapter/api/rdto/agent/req"
	"github.com/kweaver-ai/decision-agent/agent-app/src/infra/apierr"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/capierr"
	o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/gin-gonic/gin"
	"github.com/pkg/errors"
)

func (h *agentHTTPHandler) ResumeChat(c *gin.Context) {
	req := &agentreq.ResumeReq{}
	if err := c.ShouldBindJSON(req); err != nil {
		o11y.Error(c, fmt.Sprintf("[ResumeChat] should bind json error: %v", err))
		h.logger.Errorf("[ResumeChat] should bind json error: %v", err)
		rest.ReplyError(c, capierr.New400Err(c, err.Error()))

		return
	}

	channel, err := h.agentSvc.ResumeChat(c.Request.Context(), req.ConversationID)
	if err != nil {
		o11y.Error(c, fmt.Sprintf("[ResumeChat] resume chat error: %v", err))
		h.logger.Errorf("[ResumeChat] resume chat error cause: %v,err trace: %+v\n", errors.Cause(err), err)
		httpErr := rest.NewHTTPError(c.Request.Context(), http.StatusInternalServerError, apierr.AgentAPP_Agent_ResumeFailed).WithErrorDetails(err.Error())
		rest.ReplyError(c, httpErr)

		return
	}

	defer func() {
		// NOTE: 恢复会话结束后，关闭信号,或者报错中断之后，也要把信号关闭；
		session, ok := agentsvc.SessionMap.Load(req.ConversationID)
		if ok {
			session.(*agentsvc.Session).SetIsResuming(false)
		}
	}()

	c.Header("Content-Type", "text/event-stream")
	c.Header("Cache-Control", "no-cache")
	c.Header("Connection", "keep-alive")
	c.Header("Access-Control-Allow-Origin", "*")

	done := make(chan struct{})

	go func() {
		defer close(done)

		for data := range channel {
			_, err = c.Writer.Write(data)
			if err != nil {
				h.logger.Errorf("write stream data err: %v", err)
				break
			}

			c.Writer.Flush()

			if strings.HasPrefix(string(data), constant.DataEventEndStr) {
				break
			}
		}
	}()
	<-done
}
