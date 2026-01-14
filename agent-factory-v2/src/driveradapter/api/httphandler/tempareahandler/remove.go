package tempareahandler

import (
	"fmt"
	"net/http"

	tempareareq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/temparea/req"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/apierr"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/capierr"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/gin-gonic/gin"
)

func (h *tempareaHTTPHandler) Remove(c *gin.Context) {
	var req tempareareq.RemoveReq

	sourceIds := c.QueryArray("source_id")
	if len(sourceIds) == 0 {
		rest.ReplyError(c, capierr.New400Err(c, "source id is required"))
		return
	}

	req.SourceIDs = sourceIds

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

	err := h.tempareaSvc.Remove(c.Request.Context(), req)
	if err != nil {
		rest.ReplyError(c, rest.NewHTTPError(c.Request.Context(), http.StatusInternalServerError, apierr.AgentAPP_InternalError).WithErrorDetails(
			fmt.Sprintf("remove temp area failed:%s", err.Error())))
		return
	}

	rest.ReplyOK(c, http.StatusNoContent, "")
}
