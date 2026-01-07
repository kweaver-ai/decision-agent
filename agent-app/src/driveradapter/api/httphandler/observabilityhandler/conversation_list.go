package observabilityhandler

import (
	"fmt"
	"net/http"

	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/capierr"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/cenum"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper"
	o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
	"github.com/kweaver-ai/kweaver-go-lib/rest"

	"github.com/gin-gonic/gin"

	conversationresp "github.com/kweaver-ai/decision-agent/agent-app/src/driveradapter/api/rdto/conversation/conversationresp"
	observabilityreq "github.com/kweaver-ai/decision-agent/agent-app/src/driveradapter/api/rdto/observability/req"
	observabilityresp "github.com/kweaver-ai/decision-agent/agent-app/src/driveradapter/api/rdto/observability/resp"
)

var _ conversationresp.ConversationDetail
var _ observabilityresp.ObservabilityConversationDetail

func (h *observabilityHTTPHandler) ConversationList(c *gin.Context) {
	// 1. 获取路径参数
	agentID := c.Param("agent_id")
	if agentID == "" {
		h.logger.Errorf("[ConversationList] agent_id is required")
		o11y.Error(c, "[ConversationList] agent_id is required")
		httpErr := capierr.New400Err(c, "[ConversationList] agent_id is required")
		rest.ReplyError(c, httpErr)

		return
	}

	// 2. 获取请求参数
	var req observabilityreq.ConversationListReq
	if err := c.ShouldBindJSON(&req); err != nil {
		h.logger.Errorf("[ConversationList] should bind json err: %v", err)
		o11y.Error(c, fmt.Sprintf("[ConversationList] should bind json err: %v", err))
		httpErr := capierr.New400Err(c, fmt.Sprintf("[ConversationList] should bind json err: %v", err))
		rest.ReplyError(c, httpErr)

		return
	}

	// 3. 设置路径参数到请求中
	// req.AgentID = agentID
	//这里不需要设置，因为路径参数中是agent_key ，通过agent_key 获取到 对话的 记录列表，而不是debug 的列表

	// 4. 参数验证
	if req.Size <= 0 {
		req.Size = 10
	}

	if req.Page <= 0 {
		req.Page = 1
	}

	if req.StartTime > req.EndTime {
		h.logger.Errorf("[ConversationList] start_time must be less than end_time")
		o11y.Error(c, "[ConversationList] start_time must be less than end_time")
		httpErr := capierr.New400Err(c, "[ConversationList] start_time must be less than end_time")
		rest.ReplyError(c, httpErr)
		return
	}

	// // 设置时间范围默认值
	// if req.StartTime == 0 || req.EndTime == 0 {
	// 	// 如果未设置时间范围，默认查询最近30天
	// 	now := time.Now().UnixMilli()
	// 	if req.StartTime == 0 {
	// 		req.StartTime = now - 30*24*60*60*1000 // 30天前
	// 	}
	// 	if req.EndTime == 0 {
	// 		req.EndTime = now
	// 	}
	// }

	// 4. 获取用户信息
	user := chelper.GetVisitorFromCtx(c)
	if user == nil {
		httpErr := capierr.New404Err(c, "[ConversationList] user not found")
		o11y.Error(c, "[ConversationList] user not found")
		h.logger.Errorf("[ConversationList] user not found: %v", httpErr)
		rest.ReplyError(c, httpErr)

		return
	}

	// 5. 调用服务
	//agentID 值实际为 agent key
	//req.AgentID 值实际为 agent ID
	data, totalCount, err := h.conversationSvc.ListByAgentID(c.Request.Context(), agentID, req.Title, req.Page, req.Size, req.StartTime, req.EndTime)
	if err != nil {
		h.logger.Errorf("[ConversationList] call conversation service error: %v", err)
		o11y.Error(c, fmt.Sprintf("[ConversationList] call conversation service error: %v", err))
		httpErr := capierr.New500Err(c, fmt.Sprintf("[ConversationList] call conversation service error: %v", err))
		rest.ReplyError(c, httpErr)

		return
	}

	// 6. 批量查询所有conversation的session数量
	entries := make([]observabilityresp.ObservabilityConversationDetail, len(data))

	// 收集conversation IDs
	conversationIDs := make([]string, len(data))
	for i, conv := range data {
		conversationIDs[i] = conv.ID
	}

	// 批量获取session数量
	sessionCounts := make(map[string]int)

	if len(conversationIDs) > 0 {
		// 转换账户类型
		var xAccountType cenum.AccountType

		xAccountType.LoadFromMDLVisitorType(user.Type)

		counts, err := h.observabilitySvc.GetSessionCountsByConversationIDs(c.Request.Context(), req.AgentID, conversationIDs, req.StartTime, req.EndTime, user.ID, string(xAccountType))
		if err != nil {
			h.logger.Errorf("[ConversationList] batch get session counts error: %v", err)
			// 不返回错误，继续处理，所有sessionCount保持为0
		} else {
			sessionCounts = counts
		}
	}

	// 构建响应条目
	for i, conv := range data {
		sessionCount := sessionCounts[conv.ID]
		entries[i] = observabilityresp.ObservabilityConversationDetail{
			Conversation: conv,
			SessionCount: sessionCount,
		}
	}

	resp := observabilityresp.ConversationListResp{
		Entries:    entries,
		TotalCount: totalCount,
	}

	c.JSON(http.StatusOK, resp)
}
