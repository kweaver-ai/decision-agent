package v2agentexecutoraccess

import (
	"context"
	"fmt"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/v2agentexecutoraccess/v2agentexecutordto"
	o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
	"go.opentelemetry.io/otel/attribute"
)

// Resume 恢复 Agent 执行（中断后恢复）
func (ae *v2AgentExecutorHttpAcc) Resume(ctx context.Context, req *v2agentexecutordto.V2AgentResumeReq) (chan string, chan error, error) {
	var err error

	ctx, _ = o11y.StartInternalSpan(ctx)
	defer o11y.EndSpan(ctx, err)
	o11y.SetAttributes(ctx, attribute.String("agent_run_id", req.AgentRunID))
	o11y.SetAttributes(ctx, attribute.String("action", req.ResumeInfo.Action))

	url := fmt.Sprintf("%s/api/agent-executor/v2/agent/resume", ae.privateAddress)

	headers := make(map[string]string)

	messages, errs, err := ae.streamClient.StreamPost(ctx, url, headers, req)

	return messages, errs, err
}

// Terminate 终止 Agent 执行
func (ae *v2AgentExecutorHttpAcc) Terminate(ctx context.Context, req *v2agentexecutordto.V2AgentTerminateReq) error {
	var err error

	ctx, _ = o11y.StartInternalSpan(ctx)
	defer o11y.EndSpan(ctx, err)
	o11y.SetAttributes(ctx, attribute.String("agent_run_id", req.AgentRunID))

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
