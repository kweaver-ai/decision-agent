package v2agentexecutoraccess

import (
	"context"
	"fmt"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/v2agentexecutoraccess/v2agentexecutordto"
	otelTrace "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry/trace"
	"go.opentelemetry.io/otel/attribute"
)

// Terminate 终止 Agent 执行
func (ae *v2AgentExecutorHttpAcc) Terminate(ctx context.Context, req *v2agentexecutordto.AgentTerminateReq) error {
	var err error

	ctx, _ = otelTrace.StartInternalSpan(ctx)
	defer otelTrace.EndSpan(ctx, err)
	otelTrace.SetAttributes(ctx, attribute.String("agent_run_id", req.AgentRunID))

	url := fmt.Sprintf("%s/api/agent-executor/v2/agent/terminate", ae.privateAddress)

	headers := make(map[string]string)

	// 使用 streamClient 发起请求并等待完成
	messages, errs, err := ae.streamClient.StreamPost(ctx, url, headers, req)
	if err != nil {
		return err
	}

	// 等待响应完成
	for {
		select {
		case _, ok := <-messages:
			if !ok {
				return nil
			}
		case err, ok := <-errs:
			if ok && err != nil {
				return err
			}

			return nil
		}
	}
}
