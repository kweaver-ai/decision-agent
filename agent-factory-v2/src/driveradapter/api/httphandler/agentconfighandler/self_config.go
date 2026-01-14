package v3agentconfighandler

import (
	"net/http"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent_config/agentconfigresp"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/gin-gonic/gin"
)

func (h *daConfHTTPHandler) SelfConfig(c *gin.Context) {
	// 1. 创建自配置字段对象
	sf := agentconfigresp.NewSelfConfigField()

	// 2. 从内嵌JSON加载配置字段
	err := sf.LoadFromJSONStr()
	if err != nil {
		rest.ReplyError(c, err)
		return
	}

	// 3. 返回结果
	c.JSON(http.StatusOK, sf)
}
