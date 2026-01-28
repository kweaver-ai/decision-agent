package isandboxhtpp

import (
	"context"

	sandboxdto "github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/sandboxplatformhttp/sandboxplatformdto"
)

// ISandboxPlatform Sandbox Platform 接口
type ISandboxPlatform interface {
	// CreateSession 创建 Sandbox Session
	CreateSession(ctx context.Context, req sandboxdto.CreateSessionReq) (*sandboxdto.CreateSessionResp, error)
	// GetSession 获取 Sandbox Session 信息
	GetSession(ctx context.Context, sessionID string) (*sandboxdto.GetSessionResp, error)
	// DeleteSession 删除 Sandbox Session
	DeleteSession(ctx context.Context, sessionID string) error
	// DeleteConversationFiles 删除指定 Conversation 的文件
	DeleteConversationFiles(ctx context.Context, sessionID, conversationID string) error
	// ListFiles 列出指定目录下的文件
	ListFiles(ctx context.Context, sessionID, conversationID, subdir string) ([]string, error)
}
