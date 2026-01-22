package agentsvc

import (
	"context"
	"fmt"

	"github.com/bytedance/sonic"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/agentrespvo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/conversationmsgvo"
	agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
	"github.com/pkg/errors"
	"go.opentelemetry.io/otel/attribute"
)

func (agentSvc *agentSvc) handleProgress(ctx context.Context, req *agentreq.ChatReq, progresses []*agentrespvo.Progress) ([]*agentrespvo.Progress, error) {
	ctx, _ = o11y.StartInternalSpan(ctx)
	defer o11y.EndSpan(ctx, nil)
	o11y.SetAttributes(ctx, attribute.String("agent_run_id", req.AgentRunID))
	o11y.SetAttributes(ctx, attribute.String("agent_id", req.AgentID))
	o11y.SetAttributes(ctx, attribute.String("user_id", req.UserID))
	setInterface, _ := progressSet.Load(req.AssistantMessageID)

	// 1. 初始化 set
	set, _ := setInterface.(map[string]bool)
	if set == nil {
		set = make(map[string]bool)
		progressSet.Store(req.AssistantMessageID, set)
		agentSvc.logger.Infof("[handleProgress] progressSet is nil, store new set for assistantMessageID: %s", req.AssistantMessageID)
	}

	var currentProgress *agentrespvo.Progress

	// 2. 遍历 progresses
	for _, progress := range progresses {
		if progress.Status == "completed" || progress.Status == "failed" {
			if _, ok := set[progress.ID]; !ok {
				if v, ok := progressMap.Load(req.AssistantMessageID); !ok {
					progressMap.Store(req.AssistantMessageID, []*agentrespvo.Progress{progress})
				} else {
					progressMap.Store(req.AssistantMessageID, append(v.([]*agentrespvo.Progress), progress))
				}

				set[progress.ID] = true
			}
		} else if progress.Status == "processing" {
			currentProgress = progress
		}
	}

	// 3. NOTE： 如果是中断，还需要将中断前的结果拿到并拼接
	ans, err := agentSvc.forResumeInterrupt(ctx, req)
	if err != nil {
		return nil, err
	}

	// 4. append
	if v, ok := progressMap.Load(req.AssistantMessageID); ok {
		ans = append(ans, v.([]*agentrespvo.Progress)...)
	}

	// 5. append currentProgress
	if currentProgress != nil {
		ans = append(ans, currentProgress)
	}

	return ans, nil
}

func (agentSvc *agentSvc) forResumeInterrupt(ctx context.Context, req *agentreq.ChatReq) (ans []*agentrespvo.Progress, err error) {
	ans = make([]*agentrespvo.Progress, 0)

	if req.InterruptedAssistantMsgID != "" {

		var assistantMsgPO *dapo.ConversationMsgPO

		// 1. 获取中断前的消息
		assistantMsgPO, err = agentSvc.conversationMsgRepo.GetByID(ctx, req.InterruptedAssistantMsgID)
		if err != nil {
			err = errors.Wrapf(err, "[handleProgress] get interrupted progress err")
			return
		}

		// 2. 初始化 content 以避免 nil
		content := conversationmsgvo.AssistantContent{
			MiddleAnswer: &conversationmsgvo.MiddleAnswer{}, // 新增：初始化 MiddleAnswer
		}

		// 3. 得到 中断前的消息的content
		// NOTE: 不能将空字符串反序列化，否则会报错
		if assistantMsgPO.Content != nil && *assistantMsgPO.Content != "" {
			err = sonic.Unmarshal([]byte(*assistantMsgPO.Content), &content)
			if err != nil {
				o11y.Error(ctx, fmt.Sprintf("[handleProgress] unmarshal assistant content error, id: %s, err: %v", req.InterruptedAssistantMsgID, err))
				err = errors.Wrapf(err, "[handleProgress] unmarshal assistant content error, id: %s, err: %v", req.InterruptedAssistantMsgID, err)
				return
			}
		}

		// 4. 将中断前的消息的progress append到当前ans
		if content.MiddleAnswer != nil {
			ans = append(ans, content.MiddleAnswer.Progress...)
		} else {
			agentSvc.logger.Warnf("[handleProgress] skipped appending progress for interrupted msg %s: MiddleAnswer is nil", req.InterruptedAssistantMsgID)
		}
	}

	return
}
