package conversationreq

import "github.com/kweaver-ai/decision-agent/agent-app/src/driveradapter/api/rdto/common"

type ListReq struct {
	AgentAPPKey string `json:"-"`
	UserId      string `json:"-"`
	Title       string `json:"title"`
	common.PageSize
}
