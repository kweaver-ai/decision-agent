package tempareahandler

import (
	"net/http"

	tempareareq "github.com/kweaver-ai/decision-agent/agent-app/src/driveradapter/api/rdto/temparea/req"
	"github.com/kweaver-ai/decision-agent/agent-app/src/infra/apierr"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/capierr"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/gin-gonic/gin"
)

// Get 获取临时区域文件详情
func (h *tempareaHTTPHandler) Get(c *gin.Context) {
	var req tempareareq.GetReq
	req.TempAreaID = c.Param("id")

	res, err := h.tempareaSvc.Get(c.Request.Context(), req)
	if err != nil {
		rest.ReplyError(c, rest.NewHTTPError(c.Request.Context(), http.StatusInternalServerError, apierr.TempAreaGetFailed).WithErrorDetails(err.Error()))
		return
	}

	if len(res) == 0 {
		rest.ReplyError(c, capierr.New400Err(c, "temp area not found"))
		return
	}

	rest.ReplyOK(c, http.StatusOK, res)
}
