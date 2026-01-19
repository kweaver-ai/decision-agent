package tplhandler

import (
	"net/http"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/ginhelper"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/gin-gonic/gin"
)

func (h *daTplHTTPHandler) Detail(c *gin.Context) {
	// 接收语言标识转换为 context.Context
	ctx := rest.GetLanguageCtx(c)

	tplID, err := ginhelper.GetParmIDInt64(c)
	if err != nil {
		_ = c.Error(err)
		return
	}

	detail, err := h.daTplSvc.Detail(ctx, tplID)
	if err != nil {
		_ = c.Error(err)
		return
	}

	rest.ReplyOK(c, http.StatusOK, detail)
}
