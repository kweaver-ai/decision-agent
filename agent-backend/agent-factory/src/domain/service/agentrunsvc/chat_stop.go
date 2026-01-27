package agentsvc

import (
	"context"

	"github.com/bytedance/sonic"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
	agentresp "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/resp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	otelHelper "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry"
	otelTrace "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry/trace"
	"github.com/pkg/errors"
	"go.opentelemetry.io/otel/attribute"
)

// NOTE: 处理终止信号，对话终止时，进行 助手消息的持久化
func (agentSvc *agentSvc) HandleStopChan(ctx context.Context, req *agentreq.ChatReq, session *Session) error {
	var err error

	ctx, _ = otelTrace.StartInternalSpan(ctx)
	defer otelTrace.EndSpan(ctx, err)
	otelTrace.SetAttributes(ctx, attribute.String("agent_id", req.AgentID))
	otelTrace.SetAttributes(ctx, attribute.String("agent_run_id", req.AgentRunID))
	otelTrace.SetAttributes(ctx, attribute.String("user_id", req.UserID))

	msgResp := session.GetTempMsgResp()
	bytes, _ := sonic.Marshal(msgResp)

	var resp agentresp.ChatResp

	err = sonic.Unmarshal(bytes, &resp)
	if err != nil {
		otelHelper.Errorf(ctx, "[HandleStopChan] unmarshal msgResp err: %v", err)
		return errors.Wrapf(err, "[HandleStopChan] unmarshal msgResp err")
	}

	// NOTE: 将msgResp转换为msgPO
	msgPO, _, err := agentSvc.MsgResp2MsgPO(ctx, resp, req)
	if err != nil {
		otelHelper.Errorf(ctx, "[HandleStopChan] convert msgResp to msgPO err: %v", err)
		return errors.Wrapf(err, "[HandleStopChan] convert msgResp to msgPO err")
	}

	msgPO.Status = cdaenum.MsgStatusCancelled
	msgPO.UpdateTime = cutil.GetCurrentMSTimestamp()

	err = agentSvc.conversationMsgRepo.Update(ctx, &msgPO)
	if err != nil {
		otelHelper.Errorf(ctx, "[HandleStopChan] update msgPO err: %v", err)
		return errors.Wrapf(err, "[HandleStopChan] update msgPO err")
	}
	// 更新会话
	conversationPO, err := agentSvc.conversationRepo.GetByID(ctx, req.ConversationID)
	if err != nil {
		otelHelper.Errorf(ctx, "[HandleStopChan] get conversationPO err: %v", err)
		return errors.Wrapf(err, "[HandleStopChan] get conversationPO err")
	}

	conversationPO.UpdateTime = cutil.GetCurrentMSTimestamp()
	conversationPO.MessageIndex = msgPO.Index

	err = agentSvc.conversationRepo.Update(ctx, conversationPO)
	if err != nil {
		otelHelper.Errorf(ctx, "[HandleStopChan] update conversationPO err: %v", err)
		return errors.Wrapf(err, "[HandleStopChan] update conversationPO err")
	}

	otelHelper.Info(ctx, "[HandleStopChan] terminate chat success")

	return nil
}
