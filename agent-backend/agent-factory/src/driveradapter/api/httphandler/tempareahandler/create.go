package tempareahandler

import (
	"net/http"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/capierr"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/gin-gonic/gin"
	"github.com/pkg/errors"

	tempareareq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/temparea/req"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/apierr"
)

func (h *tempareaHTTPHandler) Create(c *gin.Context) {
	var req tempareareq.CreateReq
	if err := c.ShouldBindJSON(&req); err != nil {
		h.logger.Errorf("should bind json error: %v", errors.Cause(err))
		rest.ReplyError(c, capierr.New400Err(c, err.Error()))

		return
	}

	user := chelper.GetVisitorFromCtx(c)
	if user == nil {
		rest.ReplyError(c, capierr.New401Err(c, "user not found"))
		return
	}

	req.UserID = user.ID

	id, resp, err := h.tempareaSvc.Create(c.Request.Context(), req)
	if err != nil {
		rest.ReplyError(c, rest.NewHTTPError(c.Request.Context(), http.StatusInternalServerError, apierr.TempAreaCreateFailed).WithErrorDetails(err.Error()))
		return
	}

	resultMap := map[string]any{
		"id":      id,
		"sources": resp,
	}
	rest.ReplyOK(c, http.StatusOK, resultMap)
}
