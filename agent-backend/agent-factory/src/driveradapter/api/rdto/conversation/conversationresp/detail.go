package conversationresp

import (
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/conversationeo"
)

type ConversationDetail struct {
	conversationeo.Conversation
	TempareaId string `json:"temparea_id"`
	Status     string `json:"status"` // 会话最新消息的状态，completed,processing,failed
}

func NewConversationDetail() *ConversationDetail {
	return &ConversationDetail{}
}

func (d *ConversationDetail) LoadFromEo(eo *conversationeo.Conversation) error {
	d.Conversation = *eo
	return nil
}
