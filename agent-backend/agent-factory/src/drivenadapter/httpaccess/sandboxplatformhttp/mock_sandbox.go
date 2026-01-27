package sandboxplatformhttp

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/port/driven/ihttpaccess/isandboxplatformhttp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp"
	sandboxdto "github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/sandboxplatformhttp/sandboxplatformdto"
)

type mockSandboxPlatform struct {
	logger icmp.Logger
}

func NewMockSandboxPlatform(logger icmp.Logger) isandboxplatformhttp.ISandboxPlatform {
	return &mockSandboxPlatform{
		logger: logger,
	}
}

func (m *mockSandboxPlatform) CreateSession(ctx context.Context, req sandboxdto.CreateSessionReq) (*sandboxdto.CreateSessionResp, error) {
	m.logger.Infof("[MockSandboxPlatform] create session: userID=%s, agentID=%s", req.UserID, req.AgentID)

	resp := &sandboxdto.CreateSessionResp{
		SessionID: "mock-session-" + req.UserID + "-" + req.AgentID,
		Status:    "running",
		CreatedAt: 0,
		TTL:       3600,
	}

	m.logger.Infof("[MockSandboxPlatform] create session success: %s", resp.SessionID)
	return resp, nil
}

func (m *mockSandboxPlatform) GetSession(ctx context.Context, sessionID string) (*sandboxdto.GetSessionResp, error) {
	m.logger.Infof("[MockSandboxPlatform] get session: %s", sessionID)

	resp := &sandboxdto.GetSessionResp{
		SessionID: sessionID,
		Status:    "running",
		CreatedAt: 0,
		TTL:       3600,
	}

	m.logger.Infof("[MockSandboxPlatform] get session success: %s, status: %s", sessionID, resp.Status)
	return resp, nil
}

func (m *mockSandboxPlatform) DeleteSession(ctx context.Context, sessionID string) error {
	m.logger.Infof("[MockSandboxPlatform] delete session: %s", sessionID)
	m.logger.Infof("[MockSandboxPlatform] delete session success: %s", sessionID)
	return nil
}

func (m *mockSandboxPlatform) DeleteConversationFiles(ctx context.Context, sessionID, conversationID string) error {
	m.logger.Infof("[MockSandboxPlatform] delete conversation files: session=%s, conversation=%s", sessionID, conversationID)
	m.logger.Infof("[MockSandboxPlatform] delete conversation files success: session=%s, conversation=%s", sessionID, conversationID)
	return nil
}

func (m *mockSandboxPlatform) ListFiles(ctx context.Context, sessionID, conversationID, subdir string) ([]string, error) {
	m.logger.Infof("[MockSandboxPlatform] list files: session=%s, conversation=%s, subdir=%s", sessionID, conversationID, subdir)

	files := []string{
		sessionID + "/file1.txt",
		sessionID + "/file2.py",
		sessionID + "/file3.json",
	}

	m.logger.Infof("[MockSandboxPlatform] list files success: found %d files", len(files))
	return files, nil
}
