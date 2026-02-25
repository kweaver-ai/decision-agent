package agentsvc

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"go.uber.org/mock/gomock"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp/cmpmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driver/iv3portdriver/v3portdrivermock"
)

// ---------- GetAPIDoc tests ----------

func TestAgentSvc_GetAPIDoc_SquareSvcError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockSquare := v3portdrivermock.NewMockISquareSvc(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)
	mockLogger.EXPECT().Errorf(gomock.Any(), gomock.Any()).AnyTimes()

	svc := &agentSvc{
		SvcBase:    service.NewSvcBase(),
		squareSvc:  mockSquare,
		logger:     mockLogger,
	}

	mockSquare.EXPECT().GetAgentInfo(gomock.Any(), gomock.Any()).Return(nil, errors.New("not found"))

	ctx := context.Background()
	req := &agentreq.GetAPIDocReq{AgentID: "a1", AgentVersion: "v1"}
	_, err := svc.GetAPIDoc(ctx, req)
	assert.Error(t, err)
}

func TestAgentSvc_GetAPIDoc_Success(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockSquare := v3portdrivermock.NewMockISquareSvc(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)
	mockLogger.EXPECT().Errorf(gomock.Any(), gomock.Any()).AnyTimes()

	svc := &agentSvc{
		SvcBase:   service.NewSvcBase(),
		squareSvc: mockSquare,
		logger:    mockLogger,
	}

	agentInfoResp := newTestAgent()
	mockSquare.EXPECT().GetAgentInfo(gomock.Any(), gomock.Any()).Return(agentInfoResp, nil)

	ctx := context.Background()
	req := &agentreq.GetAPIDocReq{AgentID: "a1", AgentVersion: "v1"}
	result, err := svc.GetAPIDoc(ctx, req)
	assert.NoError(t, err)
	assert.NotNil(t, result)
}

// ---------- ResumeChat tests ----------

func TestAgentSvc_ResumeChat_SessionNotFound(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockLogger := cmpmock.NewMockLogger(ctrl)
	mockLogger.EXPECT().Errorf(gomock.Any(), gomock.Any()).AnyTimes()

	svc := &agentSvc{
		SvcBase: service.NewSvcBase(),
		logger:  mockLogger,
	}

	ctx := context.Background()
	// Use a conversation ID that is not stored in SessionMap
	_, err := svc.ResumeChat(ctx, "conv-not-exist-999")
	assert.Error(t, err)
}

func TestAgentSvc_ResumeChat_SessionFound(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockLogger := cmpmock.NewMockLogger(ctrl)
	mockLogger.EXPECT().Errorf(gomock.Any(), gomock.Any()).AnyTimes()

	svc := &agentSvc{
		SvcBase: service.NewSvcBase(),
		logger:  mockLogger,
	}

	// Register a session
	session := &Session{ConversationID: "conv-resume-test"}
	SessionMap.Store("conv-resume-test", session)
	defer SessionMap.Delete("conv-resume-test")

	// Close the signal after a short time so the goroutine exits
	go func() {
		time.Sleep(10 * time.Millisecond)
		session.CloseSignal()
	}()

	ctx := context.Background()
	ch, err := svc.ResumeChat(ctx, "conv-resume-test")
	assert.NoError(t, err)
	assert.NotNil(t, ch)

	// Drain the channel
	for range ch {
	}
}

func TestAgentSvc_ResumeChat_SessionFoundWithExistingSignal(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockLogger := cmpmock.NewMockLogger(ctrl)
	mockLogger.EXPECT().Errorf(gomock.Any(), gomock.Any()).AnyTimes()

	svc := &agentSvc{
		SvcBase: service.NewSvcBase(),
		logger:  mockLogger,
	}

	// Register a session with pre-existing signal
	existingSignal := make(chan struct{})
	session := &Session{ConversationID: "conv-resume-existing", Signal: existingSignal}
	SessionMap.Store("conv-resume-existing", session)
	defer SessionMap.Delete("conv-resume-existing")

	// Close the signal immediately
	close(existingSignal)

	ctx := context.Background()
	ch, err := svc.ResumeChat(ctx, "conv-resume-existing")
	assert.NoError(t, err)
	assert.NotNil(t, ch)

	// Drain channel with timeout
	done := make(chan struct{})
	go func() {
		for range ch {
		}
		close(done)
	}()

	select {
	case <-done:
	case <-time.After(500 * time.Millisecond):
		t.Log("channel drain timeout (acceptable)")
	}
}
