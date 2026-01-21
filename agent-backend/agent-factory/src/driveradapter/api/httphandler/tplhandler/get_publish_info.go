package tplhandler

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/ginhelper"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
)

// GetPublishInfo 获取模板发布信息
func (h *daTplHTTPHandler) GetPublishInfo(c *gin.Context) {
	// 接收语言标识转换为 context.Context
	ctx := rest.GetLanguageCtx(c)

	tplID, err := ginhelper.GetParmIDInt64(c)
	if err != nil {
		_ = c.Error(err)

		return
	}

	res, err := h.daTplSvc.GetPublishInfo(ctx, tplID)
	if err != nil {
		_ = c.Error(err)
		return
	}

	rest.ReplyOK(c, http.StatusOK, res)
}
