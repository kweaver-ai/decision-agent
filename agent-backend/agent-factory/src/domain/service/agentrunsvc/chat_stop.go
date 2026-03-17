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

	// 添加日志，记录 msgResp.Message.Content 的值
	if msgResp.Message.Content == nil {
		o11y.Info(ctx, "[HandleStopChan] msgResp.Message.Content is nil")
	} else {
		contentBytes, _ := sonic.Marshal(msgResp.Message.Content)
		o11y.Info(ctx, fmt.Sprintf("[HandleStopChan] msgResp.Message.Content: %s", string(contentBytes)))
	}

	// 检查消息是否已经存在
	existingMsgPO, err := agentSvc.conversationMsgRepo.GetByID(ctx, req.AssistantMessageID)
	if err != nil {
		o11y.Error(ctx, fmt.Sprintf("[HandleStopChan] get message %s err: %v", req.AssistantMessageID, err))
		return errors.Wrapf(err, "[HandleStopChan] get message err")
	}

	if existingMsgPO == nil {
		o11y.Info(ctx, "[HandleStopChan] message does not exist, skip updating")
		return nil
	}

	// 添加日志，记录 existingMsgPO.Content 的值
	if existingMsgPO.Content != nil {
		o11y.Info(ctx, fmt.Sprintf("[HandleStopChan] existingMsgPO.Content: %s", *existingMsgPO.Content))
	} else {
		o11y.Info(ctx, "[HandleStopChan] existingMsgPO.Content is nil")
	}

	// 消息存在，只更新状态和时间，不覆盖内容
	o11y.Info(ctx, fmt.Sprintf("[HandleStopChan] message exists, updating status to cancelled"))
	existingMsgPO.Status = cdaenum.MsgStatusCancelled
	existingMsgPO.UpdateTime = cutil.GetCurrentMSTimestamp()
	err = agentSvc.conversationMsgRepo.Update(ctx, existingMsgPO)
	if err != nil {
		o11y.Error(ctx, fmt.Sprintf("[HandleStopChan] update message status err: %v", err))
		return errors.Wrapf(err, "[HandleStopChan] update message status err")
	}

	// 更新会话
	conversationPO, err := agentSvc.conversationRepo.GetByID(ctx, req.ConversationID)
	if err != nil {
		o11y.Error(ctx, fmt.Sprintf("[HandleStopChan] get conversationPO err: %v", err))
		return errors.Wrapf(err, "[HandleStopChan] get conversationPO err")
	}

	conversationPO.UpdateTime = cutil.GetCurrentMSTimestamp()
	conversationPO.MessageIndex = req.AssistantMessageIndex

	err = agentSvc.conversationRepo.Update(ctx, conversationPO)
	if err != nil {
		o11y.Error(ctx, fmt.Sprintf("[HandleStopChan] update conversationPO err: %v", err))
		return errors.Wrapf(err, "[HandleStopChan] update conversationPO err")
	}

	o11y.Info(ctx, "[HandleStopChan] terminate chat success")

	return nil
}
