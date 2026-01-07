package tempareahandler

import (
	"net/http"

	tempareareq "github.com/kweaver-ai/decision-agent/agent-app/src/driveradapter/api/rdto/temparea/req"
	"github.com/kweaver-ai/decision-agent/agent-app/src/infra/apierr"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/capierr"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/gin-gonic/gin"
	"github.com/pkg/errors"
)

func (h *tempareaHTTPHandler) Append(c *gin.Context) {
	var req tempareareq.CreateReq
	if err := c.ShouldBindJSON(&req); err != nil {
		h.logger.Errorf("should bind json error: %v", errors.Cause(err))
		rest.ReplyError(c, capierr.New400Err(c, err.Error()))

		return
	}

	tempAreaID := c.Param("id")
	if tempAreaID == "" {
		rest.ReplyError(c, capierr.New400Err(c, "temp area id is required"))
		return
	}

	req.TempAreaID = tempAreaID

	user := chelper.GetVisitorFromCtx(c)
	if user == nil {
		rest.ReplyError(c, capierr.New401Err(c, "user not found"))
		return
	}

	req.UserID = user.ID

	resp, err := h.tempareaSvc.Append(c.Request.Context(), req)
	if err != nil {
		rest.ReplyError(c, rest.NewHTTPError(c.Request.Context(), http.StatusInternalServerError, apierr.TempAreaAppendFailed).WithErrorDetails(err.Error()))
		return
	}

	rest.ReplyOK(c, http.StatusOK, resp)
}
