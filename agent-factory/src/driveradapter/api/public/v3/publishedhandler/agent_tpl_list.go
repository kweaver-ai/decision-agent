package publishedhandler

import (
	"net/http"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/published/pubedreq"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/capierr"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/gin-gonic/gin"
)

// PubedTplList 已发布模板列表
func (h *publishedHandler) PubedTplList(c *gin.Context) {
	// 接收语言标识转换为 context.Context
	ctx := rest.GetLanguageCtx(c)

	// 构建请求参数
	req := pubedreq.PubedTplListReq{}
	if err := c.ShouldBindQuery(&req); err != nil {
		httpErr := capierr.New400Err(c, chelper.ErrMsg(err, &req))
		_ = c.Error(httpErr)

		return
	}

	err := req.LoadMarkerStr()
	if err != nil {
		httpErr := capierr.New400Err(c, err.Error())
		_ = c.Error(httpErr)

		return
	}

	// 调用service层获取已发布模板列表
	resp, err := h.publishedSvc.GetPubedTplList(ctx, &req)
	if err != nil {
		httpErr := capierr.New500Err(c, err.Error())
		_ = c.Error(httpErr)

		return
	}

	// 返回成功
	rest.ReplyOK(c, http.StatusOK, resp)
}
