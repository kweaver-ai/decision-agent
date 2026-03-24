package agentsvc

import (
	"context"
	"fmt"

	"github.com/bytedance/sonic"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
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

	msgResp := session.GetTempMsgResp()

	if msgResp.Message.Content == nil {
		o11y.Info(ctx, "[HandleStopChan] msgResp.Message.Content is nil")
		agentSvc.logger.Infof("[HandleStopChan] msgResp.Message.Content is nil")
	} else {
		contentBytes, err := sonic.Marshal(msgResp.Message.Content)
		if err != nil {
			o11y.Error(ctx, fmt.Sprintf("[HandleStopChan] marshal msgResp.Message.Content err: %v", err))
			return errors.Wrapf(err, "[HandleStopChan] marshal msgResp.Message.Content err")
		}

		o11y.Info(ctx, fmt.Sprintf("[HandleStopChan] msgResp.Message.Content: %s", string(contentBytes)))
	}

	existingMsgPO, err := agentSvc.conversationMsgRepo.GetByID(ctx, req.AssistantMessageID)
	if err != nil {
		o11y.Error(ctx, fmt.Sprintf("[HandleStopChan] get message %s err: %v", req.AssistantMessageID, err))
		return errors.Wrapf(err, "[HandleStopChan] get message err")
	}

	if existingMsgPO == nil {
		o11y.Info(ctx, "[HandleStopChan] message does not exist, creating new message")
		agentSvc.logger.Infof("[HandleStopChan] message does not exist, creating new message")

		msgPO, _, err := agentSvc.MsgResp2MsgPO(ctx, msgResp, req)
		if err != nil {
			o11y.Error(ctx, fmt.Sprintf("[HandleStopChan] convert msgResp to msgPO err: %v", err))
			return errors.Wrapf(err, "[HandleStopChan] convert msgResp to msgPO err")
		}

		msgPO.Status = cdaenum.MsgStatusCancelled
		msgPO.UpdateTime = cutil.GetCurrentMSTimestamp()

		_, err = agentSvc.conversationMsgRepo.Create(ctx, &msgPO)
		if err != nil {
			o11y.Error(ctx, fmt.Sprintf("[HandleStopChan] create message err: %v", err))
			return errors.Wrapf(err, "[HandleStopChan] create message err")
		}
	} else {
		if existingMsgPO.Content != nil {
			o11y.Info(ctx, fmt.Sprintf("[HandleStopChan] existingMsgPO.Content: %s", *existingMsgPO.Content))
		} else {
			o11y.Info(ctx, "[HandleStopChan] existingMsgPO.Content is nil")
			agentSvc.logger.Infof("[HandleStopChan] existingMsgPO.Content is nil")
		}

		msgPO, _, err := agentSvc.MsgResp2MsgPO(ctx, msgResp, req)
		if err != nil {
			o11y.Error(ctx, fmt.Sprintf("[HandleStopChan] convert msgResp to msgPO err: %v", err))
			return errors.Wrapf(err, "[HandleStopChan] convert msgResp to msgPO err")
		}

		if msgPO.Content != nil {
			o11y.Info(ctx, fmt.Sprintf("[HandleStopChan] msgPO.Content: %s", *msgPO.Content))
		} else {
			o11y.Info(ctx, "[HandleStopChan] msgPO.Content is nil")
			agentSvc.logger.Infof("[HandleStopChan] msgPO.Content is nil")
		}

		existingMsgPO.Content = msgPO.Content
		existingMsgPO.ContentType = msgPO.ContentType
		existingMsgPO.Ext = msgPO.Ext
		existingMsgPO.Status = cdaenum.MsgStatusCancelled
		existingMsgPO.UpdateTime = cutil.GetCurrentMSTimestamp()

		o11y.Info(ctx, "[HandleStopChan] message exists, updating content and status to cancelled")
		agentSvc.logger.Infof("[HandleStopChan] message exists, updating content and status to cancelled")

		err = agentSvc.conversationMsgRepo.Update(ctx, existingMsgPO)
		if err != nil {
			o11y.Error(ctx, fmt.Sprintf("[HandleStopChan] update message err: %v", err))
			return errors.Wrapf(err, "[HandleStopChan] update message err")
		}
	}

	conversationPO, err := agentSvc.conversationRepo.GetByID(ctx, req.ConversationID)
	if err != nil {
		o11y.Error(ctx, fmt.Sprintf("[HandleStopChan] get conversationPO err: %v", err))
		return errors.Wrapf(err, "[HandleStopChan] get conversationPO err")
	}

	conversationPO.UpdateTime = cutil.GetCurrentMSTimestamp()
	conversationPO.MessageIndex = req.AssistantMessageIndex

	// 更新会话
	err = agentSvc.conversationRepo.Update(ctx, conversationPO)
	if err != nil {
		o11y.Error(ctx, fmt.Sprintf("[HandleStopChan] update conversationPO err: %v", err))
		return errors.Wrapf(err, "[HandleStopChan] update conversationPO err")
	}

	o11y.Info(ctx, "[HandleStopChan] terminate chat success")

	return nil
}
