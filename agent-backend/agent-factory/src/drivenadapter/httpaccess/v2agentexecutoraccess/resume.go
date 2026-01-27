package v2agentexecutoraccess

import (
	"context"
	"fmt"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/v2agentexecutoraccess/v2agentexecutordto"
	otelTrace "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry/trace"
	"go.opentelemetry.io/otel/attribute"
)

// Resume 恢复 Agent 执行（中断后恢复）
func (ae *v2AgentExecutorHttpAcc) Resume(ctx context.Context, req *v2agentexecutordto.AgentResumeReq) (chan string, chan error, error) {
	var err error

	ctx, _ = otelTrace.StartInternalSpan(ctx)
	defer otelTrace.EndSpan(ctx, err)
	otelTrace.SetAttributes(ctx, attribute.String("agent_run_id", req.AgentRunID))
	otelTrace.SetAttributes(ctx, attribute.String("action", req.ResumeInfo.Action))

	url := fmt.Sprintf("%s/api/agent-executor/v2/agent/resume", ae.privateAddress)

	headers := make(map[string]string)

	messages, errs, err := ae.streamClient.StreamPost(ctx, url, headers, req)

	return messages, errs, err
}
