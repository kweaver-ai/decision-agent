package v3agentconfighandler

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/capierr"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
)

// Detail 获取Agent详情
// @Summary      获取Agent详情
// @Description  根据 Agent ID 获取 Agent 配置详细信息
// @Tags         AgentConfig
// @Accept       json
// @Produce      json
// @Param        agent_id path      string  true  "Agent ID"
// @Success      200       {object}  agentconfigresp.DetailRes  "成功"
// @Failure      400      {object}  swagger.APIError  "请求参数错误"
// @Failure      404      {object}  swagger.APIError  "Agent不存在"
// @Failure      500      {object}  swagger.APIError  "服务器内部错误"
// @Router       /v3/agent/{agent_id} [get]
// @Security     BearerAuth
func (h *daConfHTTPHandler) Detail(c *gin.Context) {
	// 1. 获取id
	id := c.Param("agent_id")
	if id == "" {
		err := capierr.New400Err(c, "id is empty")
		rest.ReplyError(c, err)

		return
	}

	// 2. 获取详情
	res, err := h.daConfSvc.Detail(c, id, "")
	if err != nil {
		rest.ReplyError(c, err)
		return
	}

	// 3. 返回结果
	c.JSON(http.StatusOK, res)
}

func (h *daConfHTTPHandler) DetailByKey(c *gin.Context) {
	// 1. 获取key
	key := c.Param("key")
	if key == "" {
		err := capierr.New400Err(c, "key is empty")
		rest.ReplyError(c, err)

		return
	}

	//---用于某个东西的测试 start---
	//tmp:=agentconfigresp.NewDetailRes()
	//
	// tmp.Key=key
	//c.JSON(http.StatusOK,tmp)
	//return
	//---用于某个东西的测试 end---

	// 2. 获取详情
	res, err := h.daConfSvc.Detail(c, "", key)
	if err != nil {
		rest.ReplyError(c, err)
		return
	}

	// 3. 返回结果
	c.JSON(http.StatusOK, res)
}
