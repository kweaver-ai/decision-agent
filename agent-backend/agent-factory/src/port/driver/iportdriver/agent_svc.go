package iportdriver

import (
	"context"

	agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
	agentresp "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/resp"
)

//go:generate mockgen -source=./agent_svc.go -destination ./iportdrivermock/agent_svc.go -package iportdrivermock
type IAgent interface {
	Chat(ctx context.Context, req *agentreq.ChatReq) (chan []byte, error)
	// ResumeChat 恢复聊天
	// 如果 resumeInterruptInfo != nil，走中断恢复逻辑
	// 如果 resumeInterruptInfo == nil，走原有逻辑
	ResumeChat(ctx context.Context, conversationID string, agentRunID string, resumeInterruptInfo *agentreq.ResumeInterruptInfo) (chan []byte, error)
	// TerminateChat 终止聊天
	// 如果 agentRunID 不为空，先调用 Executor 终止，再执行原有逻辑
	TerminateChat(ctx context.Context, conversationID string, agentRunID string) error
	GetAPIDoc(ctx context.Context, req *agentreq.GetAPIDocReq) (interface{}, error)
	FileCheck(ctx context.Context, req *agentreq.FileCheckReq) (agentresp.FileCheckResp, error)

	// ConversationSessionInit(ctx context.Context, req *agentreq.ConversationSessionInitReq) (resp *agentresp.ConversationSessionInitResp, err error)
}
