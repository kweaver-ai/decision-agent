package agentsvc

import (
	"context"
	"fmt"

	"github.com/bytedance/sonic"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/v2agentexecutoraccess/v2agentexecutordto"
	agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/capierr"
	o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
	"go.opentelemetry.io/otel/attribute"
)

// ResumeChat 恢复聊天
// 如果 resumeInterruptInfo != nil，走中断恢复逻辑（调用 Executor Resume 接口）
// 如果 resumeInterruptInfo == nil，走原有逻辑（SessionMap 恢复）
func (agentSvc *agentSvc) ResumeChat(ctx context.Context, conversationID string, agentRunID string, resumeInterruptInfo *agentreq.ResumeInterruptInfo) (chan []byte, error) {
	var err error

	ctx, _ = o11y.StartInternalSpan(ctx)
	defer o11y.EndSpan(ctx, err)
	o11y.SetAttributes(ctx, attribute.String("conversation_id", conversationID))
	o11y.SetAttributes(ctx, attribute.String("agent_run_id", agentRunID))

	// 判断是否为中断恢复
	if resumeInterruptInfo != nil {
		// 中断恢复：调用 Executor Resume 接口
		return agentSvc.resumeFromInterrupt(ctx, agentRunID, resumeInterruptInfo)
	}

	// 非中断恢复：保持现有逻辑
	return agentSvc.resumeFromSession(ctx, conversationID)
}

// resumeFromInterrupt 中断恢复逻辑（调用 Executor Resume 接口）
func (agentSvc *agentSvc) resumeFromInterrupt(ctx context.Context, agentRunID string, resumeInterruptInfo *agentreq.ResumeInterruptInfo) (chan []byte, error) {
	var err error

	o11y.Info(ctx, fmt.Sprintf("[resumeFromInterrupt] agent_run_id: %s, action: %s", agentRunID, resumeInterruptInfo.Action))

	// 构造 Executor Resume 请求
	req := &v2agentexecutordto.V2AgentResumeReq{
		AgentRunID: agentRunID,
		ResumeInfo: &v2agentexecutordto.V2AgentResumeInfo{
			Action: resumeInterruptInfo.Action,
		},
	}

	// 转换 ResumeHandle
	if resumeInterruptInfo.ResumeHandle != nil {
		req.ResumeInfo.ResumeHandle = &v2agentexecutordto.V2ResumeHandle{
			FrameID:       resumeInterruptInfo.ResumeHandle.FrameID,
			SnapshotID:    resumeInterruptInfo.ResumeHandle.SnapshotID,
			ResumeToken:   resumeInterruptInfo.ResumeHandle.ResumeToken,
			InterruptType: resumeInterruptInfo.ResumeHandle.InterruptType,
			CurrentBlock:  resumeInterruptInfo.ResumeHandle.CurrentBlock,
			RestartBlock:  resumeInterruptInfo.ResumeHandle.RestartBlock,
		}
	}

	// 转换 ModifiedArgs
	if len(resumeInterruptInfo.ModifiedArgs) > 0 {
		req.ResumeInfo.ModifiedArgs = make([]v2agentexecutordto.V2ModifiedArg, len(resumeInterruptInfo.ModifiedArgs))
		for i, arg := range resumeInterruptInfo.ModifiedArgs {
			req.ResumeInfo.ModifiedArgs[i] = v2agentexecutordto.V2ModifiedArg{
				Key:   arg.Key,
				Value: arg.Value,
			}
		}
	}

	// 调用 Executor Resume 接口
	messages, errs, err := agentSvc.agentExecutorV2.Resume(ctx, req)
	if err != nil {
		o11y.Error(ctx, fmt.Sprintf("[resumeFromInterrupt] resume failed: %v", err))
		return nil, capierr.New500Err(ctx, fmt.Sprintf("resume failed: %v", err))
	}

	// 转换 channel 类型
	channel := make(chan []byte)
	go func() {
		defer close(channel)
		for {
			select {
			case msg, ok := <-messages:
				if !ok {
					return
				}
				channel <- []byte(msg)
			case err, ok := <-errs:
				if ok && err != nil {
					o11y.Error(ctx, fmt.Sprintf("[resumeFromInterrupt] stream error: %v", err))
				}
				return
			}
		}
	}()

	return channel, nil
}

// resumeFromSession 原有的 Session 恢复逻辑
func (agentSvc *agentSvc) resumeFromSession(ctx context.Context, conversationID string) (chan []byte, error) {
	sessionInterface, ok := SessionMap.Load(conversationID)
	if !ok {
		o11y.Error(ctx, fmt.Sprintf("[ResumeChat] conversation_id %s not found", conversationID))
		agentSvc.logger.Errorf("[ResumeChat] conversation_id %s not found", conversationID)

		return nil, capierr.New400Err(ctx, "conversation_id not found")
	}

	session := sessionInterface.(*Session)
	session.Lock()
	defer session.Unlock()
	session.IsResuming = true
	// NOTE: 注册一个channel
	signal := make(chan struct{})
	if session.Signal == nil {
		session.Signal = signal
		SessionMap.Store(conversationID, session)
	} else {
		signal = session.Signal
	}

	channel := make(chan []byte)

	go func() {
		defer close(channel)

		oldResp := []byte(`{}`)
		seq := new(int)
		*seq = 0

		sessionInterface, ok := SessionMap.Load(conversationID)
		if !ok {
			o11y.Error(ctx, fmt.Sprintf("[ResumeChat] conversation_id %s not found", conversationID))
			agentSvc.logger.Errorf("[ResumeChat] conversation_id %s not found", conversationID)

			return
		}

		session := sessionInterface.(*Session)
		signal = session.GetSignal()

		newResp, err := sonic.Marshal(session.GetTempMsgResp())
		if err != nil {
			o11y.Error(ctx, fmt.Sprintf("[ResumeChat] marshal temp msg resp err: %v", err))
			agentSvc.logger.Errorf("[ResumeChat] marshal temp msg resp err: %v", err)

			return
		}
		// NOTE:先发送一次,把当前的tempMsgResp发送出去
		if newResp != nil {
			if err := StreamDiff(ctx, seq, oldResp, newResp, channel); err != nil {
				o11y.Error(ctx, fmt.Sprintf("[ResumeChat] stream diff err: %v", err))
				agentSvc.logger.Errorf("[ResumeChat] stream diff err: %v", err)

				return
			}
		}

		// NOTE: 监听信号，直到关闭
		for _, ok := <-signal; ok; _, ok = <-signal {
			// NOTE: 每当收到信号，就发送一条消息
			newResp, err := sonic.Marshal(session.GetTempMsgResp())
			if err != nil {
				o11y.Error(ctx, fmt.Sprintf("[ResumeChat] marshal temp msg resp err: %v", err))
				agentSvc.logger.Errorf("[ResumeChat] marshal temp msg resp err: %v", err)

				break
			}

			if len(oldResp) == 0 {
				oldResp = newResp
			} else {
				if err := StreamDiff(ctx, seq, oldResp, newResp, channel); err != nil {
					o11y.Error(ctx, fmt.Sprintf("[ResumeChat] stream diff err: %v", err))
					agentSvc.logger.Errorf("[ResumeChat] stream diff err: %v", err)

					break
				}

				oldResp = newResp
			}
		}

		emitJSON(seq, channel, []interface{}{}, nil, "end")
	}()

	return channel, nil
}
