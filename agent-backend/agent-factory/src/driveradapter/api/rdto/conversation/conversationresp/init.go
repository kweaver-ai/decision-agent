package conversationresp

import "github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/cenum"

type InitConversationResp struct {
	ID           string            `json:"id"`
	XAccountID   string            `json:"-"` // 用户ID
	XAccountType cenum.AccountType `json:"-"` // 用户类型 app/user/anonymous
}
