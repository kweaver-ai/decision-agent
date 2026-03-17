package agentsvc

import (
	"context"
	"fmt"

	"github.com/bytedance/sonic"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
	agentresp "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/resp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	dapo "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
	"github.com/pkg/errors"
	"go.opentelemetry.io/otel/attribute"
)

// NOTE: 处理终止信号，对话终止时，进行 助手消息的持久化
func (agentSvc *agentSvc) HandleStopChan(ctx context.Context, req *agentreq.ChatReq, session *Session) error {
	var err error

	ctx, _ = o11y.StartInternalSpan(ctx)
	defer o11y.EndSpan(ctx, err)
	o11y.SetAttributes(ctx, attribute.String("agent_id", req.AgentID))
	o11y.SetAttributes(ctx, attribute.String("agent_run_id", req.AgentRunID))
	o11y.SetAttributes(ctx, attribute.String("user_id", req.UserID))

	// 检查 session 是否为 nil
	if session == nil {
		o11y.Error(ctx, "[HandleStopChan] session cannot be nil")
		return errors.New("session cannot be nil")
	}

	// 首先尝试从session中获取临时消息
	msgResp := session.GetTempMsgResp()
	var msgPO dapo.ConversationMsgPO
	var exists bool

	// 如果session中的临时消息为空，从数据库中获取最新的消息状态
	if msgResp.Message.Content == "" {
		o11y.Info(ctx, "[HandleStopChan] temp msg resp is empty, trying to get from database")
		existingMsgPO, err := agentSvc.conversationMsgRepo.GetByID(ctx, req.AssistantMessageID)
		if err != nil {
			o11y.Error(ctx, fmt.Sprintf("[HandleStopChan] failed to get message %s: %v", req.AssistantMessageID, err))
			return errors.Wrapf(err, "[HandleStopChan] get existing message err")
		}
		if existingMsgPO != nil {
			msgPO = *existingMsgPO
			exists = true
			o11y.Info(ctx, "[HandleStopChan] got existing message from database")
		} else {
			o11y.Info(ctx, "[HandleStopChan] no existing message found, creating new one")
			// 初始化 msgPO 基本字段
			msgPO = dapo.ConversationMsgPO{
				ConversationID: req.ConversationID,
				AgentAPPKey:    req.AgentAPPKey,
				AgentID:        req.AgentID,
				AgentVersion:   req.AgentVersion,
				Role:           cdaenum.MsgRoleAssistant,
				Content:        new(string),
				ContentType:    cdaenum.MsgText,
				Ext:            new(string),
				CreateBy:       req.UserID,
				UpdateBy:       req.UserID,
			}
		}
	} else {
		// 从session中的临时消息转换为msgPO
		bytes, _ := sonic.Marshal(msgResp)
		var resp agentresp.ChatResp
		err = sonic.Unmarshal(bytes, &resp)
		if err != nil {
			o11y.Error(ctx, fmt.Sprintf("[HandleStopChan] unmarshal msgResp err: %v", err))
			return errors.Wrapf(err, "[HandleStopChan] unmarshal msgResp err")
		}

		msgPO, exists, err = agentSvc.MsgResp2MsgPO(ctx, resp, req)
		if err != nil {
			o11y.Error(ctx, fmt.Sprintf("[HandleStopChan] convert msgResp to msgPO err: %v", err))
			return errors.Wrapf(err, "[HandleStopChan] convert msgResp to msgPO err")
		}
	}

	// 更新消息状态为cancelled
	msgPO.Status = cdaenum.MsgStatusCancelled
	msgPO.UpdateTime = cutil.GetCurrentMSTimestamp()

	// 保存到数据库
	if exists {
		err = agentSvc.conversationMsgRepo.Update(ctx, &msgPO)
	} else {
		_, err = agentSvc.conversationMsgRepo.Create(ctx, &msgPO)
	}

	if err != nil {
		o11y.Error(ctx, fmt.Sprintf("[HandleStopChan] save msgPO err: %v", err))
		return errors.Wrapf(err, "[HandleStopChan] save msgPO err")
	}

	// 更新会话
	conversationPO, err := agentSvc.conversationRepo.GetByID(ctx, req.ConversationID)
	if err != nil {
		o11y.Error(ctx, fmt.Sprintf("[HandleStopChan] get conversationPO err: %v", err))
		return errors.Wrapf(err, "[HandleStopChan] get conversationPO err")
	}

	conversationPO.UpdateTime = cutil.GetCurrentMSTimestamp()
	conversationPO.MessageIndex = msgPO.Index

	err = agentSvc.conversationRepo.Update(ctx, conversationPO)
	if err != nil {
		o11y.Error(ctx, fmt.Sprintf("[HandleStopChan] update conversationPO err: %v", err))
		return errors.Wrapf(err, "[HandleStopChan] update conversationPO err")
	}

	o11y.Info(ctx, "[HandleStopChan] terminate chat success")

	return nil
}
