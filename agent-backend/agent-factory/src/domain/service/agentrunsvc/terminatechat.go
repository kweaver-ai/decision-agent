package agentsvc

import (
	"context"
	"fmt"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/v2agentexecutoraccess/v2agentexecutordto"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/capierr"
	otelHelper "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry"
	otelTrace "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry/trace"
	"go.opentelemetry.io/otel/attribute"
)

// TerminateChat 终止聊天
// 如果 agentRunID 不为空，先调用 Executor 终止，再执行原有逻辑
func (agentSvc *agentSvc) TerminateChat(ctx context.Context, conversationID string, agentRunID string) error {
	var err error

	ctx, _ = otelTrace.StartInternalSpan(ctx)
	defer otelTrace.EndSpan(ctx, err)
	otelTrace.SetAttributes(ctx, attribute.String("conversation_id", conversationID))
	otelTrace.SetAttributes(ctx, attribute.String("agent_run_id", agentRunID))

	// 1. 如果提供了 agentRunID，先调用 Executor 终止
	if agentRunID != "" {
		otelHelper.Info(ctx, fmt.Sprintf("[TerminateChat] calling executor terminate, agentRunID: %s", agentRunID))

		req := &v2agentexecutordto.AgentTerminateReq{
			AgentRunID: agentRunID,
		}
		if err := agentSvc.agentExecutorV2.Terminate(ctx, req); err != nil {
			otelHelper.Errorf(ctx, "[TerminateChat] executor terminate failed: %v", err)
			// 继续执行原有逻辑，不阻止 channel 关闭
		}
	}

	// 2. 执行原有的 channel 关闭逻辑
	stopchan, _ := stopChanMap.Load(conversationID)
	if stopchan == nil {
		otelHelper.Errorf(ctx, "[TerminateChat] terminate chat failed, conversationID: %s, stopchan not found", conversationID)
		agentSvc.logger.Errorf("terminate chat failed, conversationID: %s, stopchan not found", conversationID)

		return capierr.New404Err(ctx, "stopchan not found")
	}

	close(stopchan.(chan struct{}))
	stopChanMap.Delete(conversationID)
	otelHelper.Info(ctx, fmt.Sprintf("[TerminateChat] terminate chat success, conversationID: %s", conversationID))
	agentSvc.logger.Infof("terminate chat success, conversationID: %s", conversationID)

	return nil
}
