package publishedhandler

import (
	"net/http"

	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper/ginhelper"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/gin-gonic/gin"
)

// PubedTplDetail 已发布模板详情
func (h *publishedHandler) PubedTplDetail(c *gin.Context) {
	// 接收语言标识转换为 context.Context
	ctx := rest.GetLanguageCtx(c)

	publishedTplID, err := ginhelper.GetParmInt64(c, "tpl_id")
	if err != nil {
		_ = c.Error(err)
		return
	}

	detail, err := h.publishedSvc.PubedTplDetail(ctx, publishedTplID)
	if err != nil {
		_ = c.Error(err)
		return
	}

	rest.ReplyOK(c, http.StatusOK, detail)
}
