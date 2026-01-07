package otherhandler

import (
	"net/http"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent_config/agentconfigreq"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/other/otherreq"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/capierr"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/gin-gonic/gin"
	"github.com/pkg/errors"
)

func (o *otherHTTPHandler) DolphinTplList(c *gin.Context) {
	// 1. 获取请求参数
	var req otherreq.DolphinTplListReq

	if err := c.ShouldBind(&req); err != nil {
		err = capierr.New400Err(c, chelper.ErrMsg(err, &req))
		rest.ReplyError(c, err)

		return
	}

	// 1.1 config配置处理（如设置默认值等）
	err := agentconfigreq.HandleConfig(req.Config)
	if err != nil {
		err = errors.Wrap(err, "[DolphinTplList]: HandleConfig failed")
		_ = c.Error(err)

		return
	}

	//// 1.1 验证请求参数
	// if err := req.Config.ValObjCheckWithCtx(c, false); err != nil {
	//	err = capierr.New400Err(c, err.Error())
	//	rest.ReplyError(c, err)
	//
	//	return
	//}

	// 2. 调用服务层
	res, err := o.otherService.DolphinTplList(c, &req)
	if err != nil {
		rest.ReplyError(c, err)
		return
	}

	c.JSON(http.StatusOK, res)
}
