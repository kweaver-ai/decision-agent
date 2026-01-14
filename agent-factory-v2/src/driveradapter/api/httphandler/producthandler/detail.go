package producthandler

import (
	"net/http"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/capierr"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/gin-gonic/gin"
)

func (h *productHTTPHandler) Detail(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		err := capierr.New400Err(c, "id is empty")
		rest.ReplyError(c, err)

		return
	}

	res, err := h.productService.Detail(c, cutil.MustParseInt64(id))
	if err != nil {
		rest.ReplyError(c, err)
		return
	}

	c.JSON(http.StatusOK, res)
}
