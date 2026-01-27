package conversationhandler

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/apierr"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/capierr"
	otelHelper "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/pkg/errors"
)

func (h *conversationHTTPHandler) Detail(c *gin.Context) {
	// 1. 获取id
	id := c.Param("id")
	if id == "" {
		h.logger.Errorf("[Detail] id is empty")
		otelHelper.Error(c, "[Detail] id is empty")
		err := capierr.New400Err(c, "id is empty")
		rest.ReplyError(c, err)

		return
	}

	// 2. 获取详情
	res, err := h.conversationSvc.Detail(c, id)
	if err != nil {
		h.logger.Errorf("get conversation detail failed, cause: %v, err trace: %+v\n", errors.Cause(err), err)
		otelHelper.Error(c, fmt.Sprintf("get conversation detail failed, cause: %v, err trace: %+v\n", errors.Cause(err), err))
		httpErr := rest.NewHTTPError(c.Request.Context(), http.StatusInternalServerError,
			apierr.ConversationDetailFailed).WithErrorDetails(fmt.Sprintf("get conversation detail failed %s", err.Error()))
		rest.ReplyError(c, httpErr)

		return
	}

	// 3. 返回结果
	c.JSON(http.StatusOK, res)
}
