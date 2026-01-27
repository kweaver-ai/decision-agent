package sandboxplatformhttp

import (
	"context"
	"fmt"
	"net/http"

	"github.com/bytedance/sonic"
	"github.com/pkg/errors"

	sandboxdto "github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/sandboxplatformhttp/sandboxplatformdto"
)

func (s *sandboxPlatformHttpAcc) CreateSession(ctx context.Context, req sandboxdto.CreateSessionReq) (*sandboxdto.CreateSessionResp, error) {
	var resp sandboxdto.CreateSessionResp

	uri := s.baseURL + "/sessions"
	code, res, err := s.client.PostNoUnmarshal(ctx, uri, nil, req)
	if err != nil {
		s.logger.Errorf("[SandboxPlatform] create session failed: %v", err)
		return nil, errors.Wrap(err, "create sandbox session failed")
	}

	if code != http.StatusCreated && code != http.StatusOK {
		s.logger.Errorf("[SandboxPlatform] create session status code: %d, resp: %s", code, string(res))
		return nil, fmt.Errorf("create sandbox session failed: status code %d, resp %s", code, string(res))
	}

	if err := sonic.Unmarshal(res, &resp); err != nil {
		s.logger.Errorf("[SandboxPlatform] unmarshal response failed: %v", err)
		return nil, errors.Wrap(err, "unmarshal response failed")
	}

	s.logger.Infof("[SandboxPlatform] create session success: %s", resp.SessionID)
	return &resp, nil
}

func (s *sandboxPlatformHttpAcc) GetSession(ctx context.Context, sessionID string) (*sandboxdto.GetSessionResp, error) {
	var resp sandboxdto.GetSessionResp

	uri := s.baseURL + "/sessions/" + sessionID
	code, res, err := s.client.GetNoUnmarshal(ctx, uri, nil, nil)
	if err != nil {
		s.logger.Errorf("[SandboxPlatform] get session failed: %v", err)
		return nil, errors.Wrap(err, "get sandbox session failed")
	}

	if code != http.StatusOK {
		s.logger.Errorf("[SandboxPlatform] get session status code: %d, resp: %s", code, string(res))
		return nil, fmt.Errorf("get sandbox session failed: status code %d, resp %s", code, string(res))
	}

	if err := sonic.Unmarshal(res, &resp); err != nil {
		s.logger.Errorf("[SandboxPlatform] unmarshal response failed: %v", err)
		return nil, errors.Wrap(err, "unmarshal response failed")
	}

	s.logger.Infof("[SandboxPlatform] get session success: %s, status: %s", sessionID, resp.Status)
	return &resp, nil
}

func (s *sandboxPlatformHttpAcc) DeleteSession(ctx context.Context, sessionID string) error {
	uri := s.baseURL + "/sessions/" + sessionID
	code, res, err := s.client.DeleteNoUnmarshal(ctx, uri, nil)
	if err != nil {
		s.logger.Errorf("[SandboxPlatform] delete session failed: %v", err)
		return errors.Wrap(err, "delete sandbox session failed")
	}

	if code != http.StatusOK && code != http.StatusNoContent {
		s.logger.Errorf("[SandboxPlatform] delete session status code: %d, resp: %s", code, string(res))
		return fmt.Errorf("delete sandbox session failed: status code %d, resp %s", code, string(res))
	}

	s.logger.Infof("[SandboxPlatform] delete session success: %s", sessionID)
	return nil
}

func (s *sandboxPlatformHttpAcc) DeleteConversationFiles(ctx context.Context, sessionID, conversationID string) error {
	uri := s.baseURL + "/sessions/" + sessionID + "/conversations/" + conversationID + "/files"
	code, res, err := s.client.DeleteNoUnmarshal(ctx, uri, nil)
	if err != nil {
		s.logger.Errorf("[SandboxPlatform] delete conversation files failed: %v", err)
		return errors.Wrap(err, "delete conversation files failed")
	}

	if code != http.StatusOK && code != http.StatusNoContent {
		s.logger.Errorf("[SandboxPlatform] delete conversation files status code: %d, resp: %s", code, string(res))
		return fmt.Errorf("delete conversation files failed: status code %d, resp %s", code, string(res))
	}

	s.logger.Infof("[SandboxPlatform] delete conversation files success: session=%s, conversation=%s", sessionID, conversationID)
	return nil
}

func (s *sandboxPlatformHttpAcc) ListFiles(ctx context.Context, sessionID, conversationID, subdir string) ([]string, error) {
	var resp struct {
		Files []string `json:"files"`
	}

	uri := s.baseURL + "/sessions/" + sessionID + "/conversations/" + conversationID + "/files"
	if subdir != "" {
		uri += "?subdir=" + subdir
	}

	code, res, err := s.client.GetNoUnmarshal(ctx, uri, nil, nil)
	if err != nil {
		s.logger.Errorf("[SandboxPlatform] list files failed: %v", err)
		return nil, errors.Wrap(err, "list files failed")
	}

	if code != http.StatusOK {
		s.logger.Errorf("[SandboxPlatform] list files status code: %d, resp: %s", code, string(res))
		return nil, fmt.Errorf("list files failed: status code %d, resp %s", code, string(res))
	}

	if err := sonic.Unmarshal(res, &resp); err != nil {
		s.logger.Errorf("[SandboxPlatform] unmarshal response failed: %v", err)
		return nil, errors.Wrap(err, "unmarshal response failed")
	}

	s.logger.Infof("[SandboxPlatform] list files success: found %d files", len(resp.Files))
	return resp.Files, nil
}
