package agentsvc

import (
	"context"
	"fmt"
	"net/http"
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/constant"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service/agentrunsvc/chatlogrecord"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/agentrespvo"
	agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
	agentresp "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/resp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/session/sessionreq"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/apierr"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/capierr"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/ctype"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry/logs"
	otelTrace "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry/trace"
	o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"go.opentelemetry.io/otel/attribute"
)

var (
	// NOTE: 终止channel map， 用于终止会话，key为会话ID，value为终止channel
	stopChanMap sync.Map = sync.Map{}
	// NOTE: session map，用于对话恢复，key为会话ID，value为session
	SessionMap sync.Map = sync.Map{}
	// NOTE: key 为assistantMessageID，value 为progress的数组,存储所有状态不为processing的progress，不重复
	// progressMap map[string][]*agentrespvo.Progress = make(map[string][]*agentrespvo.Progress)
	progressMap sync.Map = sync.Map{}
	// NOTE: key 为assistantMessageID，value 为map[srting]bool ,判断一个progress的ID是否已经存在
	// progressSet map[string]map[string]bool = make(map[string]map[string]bool)
	progressSet sync.Map = sync.Map{}
)

const (
	CHANNEL_SIZE = 100
)

// NOTE: 统一的chat服务
func (agentSvc *agentSvc) Chat(ctx context.Context, req *agentreq.ChatReq) (chan []byte, error) {
	var err error

	newCtx, _ := otelTrace.StartInternalSpan(ctx)
	defer otelTrace.EndSpan(newCtx, err)
	otelTrace.SetAttributes(newCtx, attribute.String("agent_id", req.AgentID))
	otelTrace.SetAttributes(newCtx, attribute.String("agent_run_id", req.AgentRunID))
	otelTrace.SetAttributes(newCtx, attribute.String("user_id", req.UserID))

	defer func() {
		if err != nil {
			chatlogrecord.LogFailedExecution(ctx, req, err, nil)
		}
	}()

	// NOTE: 1. 根据agentID 和agentVersion 获取agent配置
	// NOTE: Chat接口请求时，agentID 实际值为agentID, APIChat接口请求时，agentID 实际值为agentKey
	agent, err := agentSvc.agentFactory.GetAgent(newCtx, req.AgentID, req.AgentVersion)
	if err != nil {
		o11y.Error(newCtx, fmt.Sprintf("[chat] get agent failed: %v", err))

		attributes := []attribute.KeyValue{}
		attributes = append(attributes, attribute.String("error", err.Error()))
		logs.LoggerFromContext(newCtx).Error(newCtx, "[chat] get agent failed: ", attributes...)

		return nil, rest.NewHTTPError(newCtx, http.StatusInternalServerError,
			apierr.AgentAPP_Agent_GetAgentFailed).WithErrorDetails(fmt.Sprintf("[chat] get agent failed: %v", err))
	}

	// NOTE：传递给AgentExecutor的agentID 前确保实际值为agentID
	req.AgentID = agent.ID

	// NOTE: 如果是apichat,但是没有发布成api agent，则返回403
	if req.CallType == constant.APIChat && agent.PublishInfo.IsAPIAgent == 0 {
		httpErr := capierr.NewCustom403Err(newCtx, apierr.AgentAPP_Forbidden_PermissionDenied, "[Chat] apichat is not published")
		return nil, httpErr
	}

	// NOTE: 2. 获取历史上下文
	conversationPO, contexts, msgIndex, err := agentSvc.GetHistoryAndMsgIndex(newCtx, req)
	if err != nil {
		o11y.Error(newCtx, fmt.Sprintf("[chat] get history and msg index failed: %v", err))
		return nil, err
	}

	// NOTE: 3. 插入用户消息和助手消息, 并返回userMessageID, assistantMessageID, assistantMessageIndex
	req.UserMessageID, req.AssistantMessageID, req.AssistantMessageIndex, err = agentSvc.UpsertUserAndAssistantMsg(newCtx, req, msgIndex, conversationPO)
	if err != nil {
		o11y.Error(newCtx, fmt.Sprintf("[chat] upsert user and assistant msg failed: %v", err))
		return nil, err
	}

	// NOTE: 4.  创建一个stop_channel 关联conversationID
	stopChan := make(chan struct{})
	stopChanMap.Store(req.ConversationID, stopChan)

	// NOTE: 5. 创建一个session 关联conversationID 用于会话恢复
	session := &Session{
		RWMutex:        sync.RWMutex{},
		ConversationID: req.ConversationID,
		TempMsgResp:    agentresp.ChatResp{},
		Signal:         nil,
		IsResuming:     false,
	}
	SessionMap.Store(req.ConversationID, session)

	progressMap.Store(req.AssistantMessageID, make([]*agentrespvo.Progress, 0))
	progressSet.Store(req.AssistantMessageID, make(map[string]bool, 0))

	// NOTE: 创建一个session
	manageReq := sessionreq.ManageReq{
		Action:         sessionreq.SessionManageActionGetInfoOrCreate,
		AgentID:        req.AgentID,
		AgentVersion:   req.AgentVersion,
		ConversationID: req.ConversationID,
	}

	startTime, _, err := agentSvc.sessionSvc.HandleGetInfoOrCreate(ctx, manageReq, &ctype.VisitorInfo{
		XAccountID:        req.XAccountID,
		XAccountType:      req.XAccountType,
		XBusinessDomainID: cenum.BizDomainID(req.XBusinessDomainID),
	}, false)
	if err != nil {
		return nil, err
	}

	// NOTE: 确保 Sandbox Session 存在并就绪
	sessionID := fmt.Sprintf("sb-session-%s", req.UserID)
	sandboxSessionID, err := agentSvc.EnsureSandboxSession(newCtx, sessionID, req)
	if err != nil {
		o11y.Error(newCtx, fmt.Sprintf("[chat] ensure sandbox session failed: %v", err))
		return nil, err
	}

	// 将 sandbox_session_id 传递给 Agent Executor
	req.SandboxSessionID = sandboxSessionID

	// NOTE: 生成ConversationSessionID
	req.ConversationSessionID = fmt.Sprintf("%s-%d", req.ConversationID, startTime)

	// NOTE: 6. 生成agent call请求
	agentCallReq, err := agentSvc.GenerateAgentCallReq(newCtx, req, contexts, agent)
	if err != nil {
		agentSvc.logger.Errorf("[Chat] generate agent call req err: %v", err)
		o11y.Error(newCtx, fmt.Sprintf("[chat] generate agent call req err: %v", err))

		return nil, err
	}

	// NOTE: 7. 调用agent-executor
	// 创建一个不带取消的ctx，复制可观测性信息
	callCtx := context.WithoutCancel(ctx)
	// 创建一个带取消的ctx，用于终止对话时取消agent-executor的请求
	cancelCtx, cancel := context.WithCancel(callCtx)

	agentCall := &AgentCall{
		callCtx:         cancelCtx,
		req:             agentCallReq,
		agentExecutorV1: agentSvc.agentExecutorV1,
		agentExecutorV2: agentSvc.agentExecutorV2,
		cancelFunc:      cancel,
	}

	messageChan, errChan, err := agentCall.Call()
	if err != nil {
		// NOTE: 发生错误，将assistantMessage 状态设置为failed
		conversationAssistantMsgPO, _ := agentSvc.conversationMsgRepo.GetByID(callCtx, req.AssistantMessageID)
		conversationAssistantMsgPO.Status = cdaenum.MsgStatusFailed
		agentSvc.conversationMsgRepo.Update(callCtx, conversationAssistantMsgPO)
		agentSvc.logger.Errorf("[Chat] call agent executor err: %v", err)
		o11y.Error(newCtx, fmt.Sprintf("[chat] call agent executor err: %v", err))

		return nil, rest.NewHTTPError(newCtx, http.StatusInternalServerError,
			apierr.AgentAPP_Agent_CallAgentExecutorFailed).WithErrorDetails(fmt.Sprintf("[chat] call agent executor err: %v", err))
	}

	// NOTE: 8. 流式响应处理
	channel := make(chan []byte, CHANNEL_SIZE)

	go agentSvc.Process(req, agent, stopChan, channel, messageChan, errChan, agentCall.Cancel)

	//NOTE: 9. 异步恢复会话
	go func() {
		manageReq := sessionreq.ManageReq{
			Action:         sessionreq.SessionManageActionRecoverLifetimeOrCreate,
			AgentID:        req.AgentID,
			AgentVersion:   req.AgentVersion,
			ConversationID: req.ConversationID,
		}

		_ctx := context.Background()

		_, _, err := agentSvc.sessionSvc.HandleRecoverLifetimeOrCreate(_ctx, manageReq, &ctype.VisitorInfo{
			XAccountID:        req.XAccountID,
			XAccountType:      req.XAccountType,
			XBusinessDomainID: cenum.BizDomainID(req.XBusinessDomainID),
		}, false)
		if err != nil {
			agentSvc.logger.Errorf("[Chat] SessionManage RecoverLifetimeOrCreate err: %v", err)
		}
	}()

	return channel, nil
}
