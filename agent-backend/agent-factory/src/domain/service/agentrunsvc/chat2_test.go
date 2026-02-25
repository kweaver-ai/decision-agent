package agentsvc

import (
	"context"
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"go.uber.org/mock/gomock"

	"github.com/kweaver-ai/decision-agent/agent-factory/conf"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
	agentexecutordto "github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/agentexecutoraccess/agentexecutordto"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp/cmpmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driver/iportdriver/iportdrivermock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driver/iv3portdriver/v3portdrivermock"
)

// Chat: agentCall.Call fails (both executors nil → "not supported" error)
func TestAgentSvc_Chat_AgentCallFailed(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockSquare := v3portdrivermock.NewMockISquareSvc(ctrl)
	mockConvRepo := idbaccessmock.NewMockIConversationRepo(ctrl)
	mockMsgRepo := idbaccessmock.NewMockIConversationMsgRepo(ctrl)
	mockSessionSvc := iportdrivermock.NewMockISessionSvc(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)
	allowAnyLoggerCalls(mockLogger)

	svc := &agentSvc{
		SvcBase:             service.NewSvcBase(),
		squareSvc:           mockSquare,
		logger:              mockLogger,
		conversationRepo:    mockConvRepo,
		conversationMsgRepo: mockMsgRepo,
		sessionSvc:          mockSessionSvc,
		sandboxPlatformConf: &conf.SandboxPlatformConf{},
		// agentExecutorV1 and V2 both nil → Call returns "not supported"
	}

	agentInfo := newTestAgent()
	mockSquare.EXPECT().GetAgentInfo(gomock.Any(), gomock.Any()).Return(agentInfo, nil)
	mockConvRepo.EXPECT().Create(gomock.Any(), gomock.Any()).Return(&dapo.ConversationPO{ID: "conv-call-err"}, nil)
	gomock.InOrder(
		mockMsgRepo.EXPECT().Create(gomock.Any(), gomock.Any()).Return("user-msg-2", nil),
		mockConvRepo.EXPECT().Update(gomock.Any(), gomock.Any()).Return(nil),
		mockMsgRepo.EXPECT().Create(gomock.Any(), gomock.Any()).Return("asst-msg-2", nil),
	)
	mockSessionSvc.EXPECT().HandleGetInfoOrCreate(gomock.Any(), gomock.Any(), gomock.Any(), gomock.Any()).
		Return(int64(0), 0, nil)
	// After Call() fails, GetByID + Update mark the assistant msg as failed
	mockMsgRepo.EXPECT().GetByID(gomock.Any(), "asst-msg-2").Return(&dapo.ConversationMsgPO{ID: "asst-msg-2"}, nil)
	mockMsgRepo.EXPECT().Update(gomock.Any(), gomock.Any()).Return(nil)

	ctx := context.Background()
	req := &agentreq.ChatReq{
		AgentID:       "a1",
		InternalParam: agentreq.InternalParam{UserID: "u1"},
	}
	_, err := svc.Chat(ctx, req)
	assert.Error(t, err)
}

// Chat: GenerateAgentCallReq fails (no KnowledgeRepo configured, toolset fetch ok but req generation hits error)
func TestAgentSvc_Chat_GenerateAgentCallReqError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockSquare := v3portdrivermock.NewMockISquareSvc(ctrl)
	mockConvRepo := idbaccessmock.NewMockIConversationRepo(ctrl)
	mockMsgRepo := idbaccessmock.NewMockIConversationMsgRepo(ctrl)
	mockSessionSvc := iportdrivermock.NewMockISessionSvc(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)
	allowAnyLoggerCalls(mockLogger)

	// v1 executor that errors
	v1 := &mockV1Executor{
		callFn: func(_ context.Context, _ *agentexecutordto.AgentCallReq) (chan string, chan error, error) {
			return nil, nil, errors.New("exec error")
		},
	}

	svc := &agentSvc{
		SvcBase:             service.NewSvcBase(),
		squareSvc:           mockSquare,
		logger:              mockLogger,
		conversationRepo:    mockConvRepo,
		conversationMsgRepo: mockMsgRepo,
		sessionSvc:          mockSessionSvc,
		agentExecutorV1:     v1,
		sandboxPlatformConf: &conf.SandboxPlatformConf{},
	}

	agentInfo := newTestAgent()
	mockSquare.EXPECT().GetAgentInfo(gomock.Any(), gomock.Any()).Return(agentInfo, nil)
	mockConvRepo.EXPECT().Create(gomock.Any(), gomock.Any()).Return(&dapo.ConversationPO{ID: "conv-req-err"}, nil)
	gomock.InOrder(
		mockMsgRepo.EXPECT().Create(gomock.Any(), gomock.Any()).Return("user-msg-3", nil),
		mockConvRepo.EXPECT().Update(gomock.Any(), gomock.Any()).Return(nil),
		mockMsgRepo.EXPECT().Create(gomock.Any(), gomock.Any()).Return("asst-msg-3", nil),
	)
	mockSessionSvc.EXPECT().HandleGetInfoOrCreate(gomock.Any(), gomock.Any(), gomock.Any(), gomock.Any()).
		Return(int64(0), 0, nil)
	// v1 executor error → Chat marks assistant msg as failed
	mockMsgRepo.EXPECT().GetByID(gomock.Any(), "asst-msg-3").Return(&dapo.ConversationMsgPO{ID: "asst-msg-3"}, nil)
	mockMsgRepo.EXPECT().Update(gomock.Any(), gomock.Any()).Return(nil)

	ctx := context.Background()
	req := &agentreq.ChatReq{
		AgentID:       "a1",
		InternalParam: agentreq.InternalParam{UserID: "u1"},
	}
	_, err := svc.Chat(ctx, req)
	assert.Error(t, err)
}
