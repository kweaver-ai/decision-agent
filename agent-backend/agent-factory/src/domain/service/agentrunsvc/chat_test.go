package agentsvc

import (
	"context"
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"go.uber.org/mock/gomock"

	"github.com/kweaver-ai/decision-agent/agent-factory/conf"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/constant"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp/cmpmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driver/iportdriver/iportdrivermock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driver/iv3portdriver/v3portdrivermock"
)

func TestAgentSvc_Chat_GetAgentInfoError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockSquare := v3portdrivermock.NewMockISquareSvc(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)
	allowAnyLoggerCalls(mockLogger)

	svc := &agentSvc{
		SvcBase:             service.NewSvcBase(),
		squareSvc:           mockSquare,
		logger:              mockLogger,
		sandboxPlatformConf: &conf.SandboxPlatformConf{},
	}

	mockSquare.EXPECT().GetAgentInfo(gomock.Any(), gomock.Any()).Return(nil, errors.New("agent not found"))

	ctx := context.Background()
	req := &agentreq.ChatReq{
		AgentID: "a1", AgentVersion: "v1",
		InternalParam: agentreq.InternalParam{UserID: "u1"},
	}
	_, err := svc.Chat(ctx, req)
	assert.Error(t, err)
}

func TestAgentSvc_Chat_APIChat_NotPublished(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockSquare := v3portdrivermock.NewMockISquareSvc(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)
	allowAnyLoggerCalls(mockLogger)

	svc := &agentSvc{
		SvcBase:             service.NewSvcBase(),
		squareSvc:           mockSquare,
		logger:              mockLogger,
		sandboxPlatformConf: &conf.SandboxPlatformConf{},
	}

	agentInfo := newTestAgent()
	agentInfo.PublishInfo.IsAPIAgent = 0
	mockSquare.EXPECT().GetAgentInfo(gomock.Any(), gomock.Any()).Return(agentInfo, nil)

	ctx := context.Background()
	req := &agentreq.ChatReq{
		AgentID: "a1",
		InternalParam: agentreq.InternalParam{
			UserID:   "u1",
			CallType: constant.APIChat,
		},
	}
	_, err := svc.Chat(ctx, req)
	assert.Error(t, err)
}

func TestAgentSvc_Chat_GetHistoryError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockSquare := v3portdrivermock.NewMockISquareSvc(ctrl)
	mockConvRepo := idbaccessmock.NewMockIConversationRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)
	allowAnyLoggerCalls(mockLogger)

	svc := &agentSvc{
		SvcBase:             service.NewSvcBase(),
		squareSvc:           mockSquare,
		logger:              mockLogger,
		conversationRepo:    mockConvRepo,
		sandboxPlatformConf: &conf.SandboxPlatformConf{},
	}

	agentInfo := newTestAgent()
	mockSquare.EXPECT().GetAgentInfo(gomock.Any(), gomock.Any()).Return(agentInfo, nil)
	mockConvRepo.EXPECT().Create(gomock.Any(), gomock.Any()).Return(nil, errors.New("db error"))

	ctx := context.Background()
	req := &agentreq.ChatReq{
		AgentID: "a1",
		InternalParam: agentreq.InternalParam{UserID: "u1"},
	}
	_, err := svc.Chat(ctx, req)
	assert.Error(t, err)
}

func TestAgentSvc_Chat_UpsertMsgError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockSquare := v3portdrivermock.NewMockISquareSvc(ctrl)
	mockConvRepo := idbaccessmock.NewMockIConversationRepo(ctrl)
	mockMsgRepo := idbaccessmock.NewMockIConversationMsgRepo(ctrl)
	mockLogger := cmpmock.NewMockLogger(ctrl)
	allowAnyLoggerCalls(mockLogger)

	svc := &agentSvc{
		SvcBase:             service.NewSvcBase(),
		squareSvc:           mockSquare,
		logger:              mockLogger,
		conversationRepo:    mockConvRepo,
		conversationMsgRepo: mockMsgRepo,
		sandboxPlatformConf: &conf.SandboxPlatformConf{},
	}

	agentInfo := newTestAgent()
	mockSquare.EXPECT().GetAgentInfo(gomock.Any(), gomock.Any()).Return(agentInfo, nil)
	mockConvRepo.EXPECT().Create(gomock.Any(), gomock.Any()).Return(&dapo.ConversationPO{ID: "conv-1"}, nil)
	mockMsgRepo.EXPECT().Create(gomock.Any(), gomock.Any()).Return("", errors.New("msg create error"))

	ctx := context.Background()
	req := &agentreq.ChatReq{
		AgentID: "a1",
		InternalParam: agentreq.InternalParam{UserID: "u1"},
	}
	_, err := svc.Chat(ctx, req)
	assert.Error(t, err)
}

func TestAgentSvc_Chat_SessionSvcError(t *testing.T) {
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
	}

	agentInfo := newTestAgent()
	mockSquare.EXPECT().GetAgentInfo(gomock.Any(), gomock.Any()).Return(agentInfo, nil)
	mockConvRepo.EXPECT().Create(gomock.Any(), gomock.Any()).Return(&dapo.ConversationPO{ID: "conv-s1"}, nil)
	gomock.InOrder(
		mockMsgRepo.EXPECT().Create(gomock.Any(), gomock.Any()).Return("user-msg-1", nil),
		mockConvRepo.EXPECT().Update(gomock.Any(), gomock.Any()).Return(nil),
		mockMsgRepo.EXPECT().Create(gomock.Any(), gomock.Any()).Return("asst-msg-1", nil),
	)
	mockSessionSvc.EXPECT().HandleGetInfoOrCreate(gomock.Any(), gomock.Any(), gomock.Any(), gomock.Any()).
		Return(int64(0), 0, errors.New("session error"))

	ctx := context.Background()
	req := &agentreq.ChatReq{
		AgentID: "a1",
		InternalParam: agentreq.InternalParam{UserID: "u1"},
	}
	_, err := svc.Chat(ctx, req)
	assert.Error(t, err)
}
