package producthandler

import (
	"net/http"

	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-factory/src/driveradapter/api/rdto/product/productreq"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/capierr"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/mdl-go-lib/rest"
	"github.com/gin-gonic/gin"
)

func (h *productHTTPHandler) List(c *gin.Context) {
	// 1. 获取请求参数
	var req productreq.ListReq

	if err := c.ShouldBind(&req); err != nil {
		err = capierr.New400Err(c, chelper.ErrMsg(err, &req))
		rest.ReplyError(c, err)

		return
	}

	// 2. 调用服务层
	res, err := h.productService.List(c, req.GetOffset(), req.GetLimit())
	if err != nil {
		rest.ReplyError(c, err)
		return
	}

	c.JSON(http.StatusOK, res)
}
