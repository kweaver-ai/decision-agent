package agentresp

import (
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/conversationmsgvo"
	// "github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/rest"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
)

// NOTE: chat的响应结果，要求和会话详情基本一致
type ChatResp struct {
	ConversationID     string `json:"conversation_id"`      // 会话ID
	UserMessageID      string `json:"user_message_id"`      // 用户消息ID
	AssistantMessageID string `json:"assistant_message_id"` // 助手消息ID

	Message conversationmsgvo.Message `json:"message"` // 消息
	// Status  string                    `json:"status"`  // 状态
	Error *rest.HTTPError `json:"error"` // 错误
}
