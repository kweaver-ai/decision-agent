package agentsvc

import (
	"context"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/bytedance/sonic"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service/agentrunsvc/chatlogrecord"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/agentfactoryaccess/agentfactorydto"
	agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
	agentresp "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/resp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/apierr"
	o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"go.opentelemetry.io/otel/attribute"
)

// NOTE: 流式处理, 接受agent-executor的返回结果,进行会话后处理，响应前端
func (agentSvc *agentSvc) Process(req *agentreq.ChatReq, agent agentfactorydto.Agent, stopChan chan struct{},
	respChan chan []byte, messageChan chan string, errChan chan error, cancelFunc func(),
) error {
	// NOTE: 记录开始时间
	startTime := time.Now()

	// NOTE: 创建流式日志记录器（仅 DEBUG 模式）
	// executorResLogger: 记录 Executor 返回的原始响应
	// processedResLogger: 记录处理后返回给前端的响应
	executorResLogger, _ := NewStreamingResponseLogger(req.ConversationID, ExecutorResponse)
	processedResLogger, _ := NewStreamingResponseLogger(req.ConversationID, ProcessedResponse)

	defer func() {
		if executorResLogger != nil {
			executorResLogger.Complete()
		}

		if processedResLogger != nil {
			processedResLogger.Complete()
		}
	}()

	var err error
	// NOTE: 使用新的ctx，确保process协程能独立完成请求，不受外界影响
	ctx := context.Background()
	ctx, _ = o11y.StartInternalSpan(ctx)

	defer o11y.EndSpan(ctx, err)
	o11y.SetAttributes(ctx, attribute.String("agent_id", req.AgentID))
	o11y.SetAttributes(ctx, attribute.String("agent_run_id", req.AgentRunID))
	o11y.SetAttributes(ctx, attribute.String("user_id", req.UserID))
	// NOTE: process是对话的核心，process结束时关闭respChan
	defer close(respChan)

	lastData := []byte(`{}`)

	var currentData []byte

	seq := new(int)
	*seq = 0
	isEnd := false

	var session *Session = &Session{}
	// failed := false
	var counter int = -1
looplabel:
	for {
		select {
		case msg, more := <-messageChan:
			if !more {
				// NOTE: 如果channel不关闭，则会导致channel阻塞
				isEnd = true
				break looplabel
			}
			var message string
			parts := strings.SplitN(msg, ":", 2)
			if len(parts) == 2 && parts[0] == "data" {
				message = parts[1]
			} else {
				agentSvc.logger.Errorf("[Process] the format of message is invalid,  msg: %v", msg)
				continue
			}
			// NOTE: 记录 Executor 返回的原始响应（仅 DEBUG 模式）
			if executorResLogger != nil {
				executorResLogger.LogChunk([]byte(message))
			}
			// NOTE: message 是原始数据
			// currentData, isEnd, err = agentSvc.CallResult2MsgResp(ctx, []byte(message), req)
			currentData, isEnd, err = agentSvc.AfterProcess(ctx, []byte(message), req, &agent)
			if err != nil {
				agentSvc.logger.Errorf("[Process] after process err: %v", err)
				o11y.Error(ctx, fmt.Sprintf("[Process] after process err: %v", err))
				isEnd = true
				break looplabel
			}
			// NOTE: 记录处理后的响应（仅 DEBUG 模式）
			if processedResLogger != nil && len(currentData) > 0 {
				processedResLogger.LogChunk(currentData)
			}
			counter++
			if counter%agentSvc.streamDiffFrequency == 0 || isEnd {
				// NOTE: 这里的currentData 是newMsgResp
				var val agentresp.ChatResp
				err = sonic.Unmarshal(currentData, &val)
				if err != nil {
					agentSvc.logger.Errorf("[Process] unmarshal currentData err: %v", err)
					o11y.Error(ctx, fmt.Sprintf("[Process] unmarshal currentData err: %v", err))
				}
				sessionInterface, ok := SessionMap.Load(req.ConversationID)
				if !ok {
					agentSvc.logger.Errorf("[Process] session not found")
					isEnd = true
					break looplabel
				}
				session = sessionInterface.(*Session)
				session.UpdateTempMsgResp(val)
				SessionMap.Store(req.ConversationID, session)
				if isEnd {
					session.CloseSignal()
				} else {
					session.SendSignal()
				}
				if req.Stream {
					if req.IncStream {
						err := StreamDiff(ctx, seq, lastData, currentData, respChan)
						if err != nil {
							agentSvc.logger.Errorf("[Process] parse event stream message err: %v", err)
							o11y.Error(ctx, fmt.Sprintf("[Process] parse event stream message err: %v", err))
						}
						lastData = currentData
					} else {
						respChan <- formatSSEMessage(string(currentData))
					}
				} else {
					// NOTE: 非流式处理
					respChan <- currentData
				}
				// NOTE: 如果isEnd为true，则结束,需要先stream diff，再结束，否则丢失最后一次的信息
				if isEnd {
					break looplabel
				}
			}

		case err, more := <-errChan:
			if !more {
				isEnd = true
				break looplabel
			}
			if req.Stream {
				if err.Error() != "unexpected EOF" && err.Error() != "EOF" {
					errMsg := rest.NewHTTPError(ctx, http.StatusInternalServerError, apierr.AgentAPP_InternalError).WithErrorDetails(err.Error())
					errBytes, _ := sonic.Marshal(errMsg)
					respChan <- formatSSEMessage(string(errBytes))
				}
				if err.Error() == "unexpected EOF" || err.Error() == "EOF" {
					isEnd = true
					break looplabel
				}
			} else {
				httpErr := rest.NewHTTPError(ctx, http.StatusInternalServerError, apierr.AgentAPP_InternalError).WithErrorDetails(err.Error())
				errBytes, _ := sonic.Marshal(httpErr)
				respChan <- errBytes
			}
		case <-stopChan:
			isEnd = true
			err := agentSvc.HandleStopChan(ctx, req, session)
			if err != nil {
				agentSvc.logger.Errorf("[Process] handle stop chan err: %v", err)
				o11y.Error(ctx, fmt.Sprintf("[Process] handle stop chan err: %v", err))
			}
			// NOTE: 取消agent-executor的请求,中断大模型输出
			cancelFunc()
			agentSvc.logger.Infof("[Process] handle stop chan success")
			break looplabel
		case <-time.After(5 * time.Second):
			agentSvc.logger.Debugf("[Process] get msg from messageChan timeout 5s")
		}
	}

	if err != nil {
		// NOTE: 发生错误，将assistantMessage 状态设置为failed
		conversationAssistantMsgPO, errNew := agentSvc.conversationMsgRepo.GetByID(ctx, req.AssistantMessageID)
		if errNew != nil {
			agentSvc.logger.Errorf("[Process] get conversation assistant message failed: %v", errNew)
			o11y.Error(ctx, fmt.Sprintf("[Process] get conversation assistant message failed: %v", errNew))
		}

		conversationAssistantMsgPO.Status = cdaenum.MsgStatusFailed
		agentSvc.conversationMsgRepo.Update(ctx, conversationAssistantMsgPO)

		// NOTE： 上报日志
		var agentResp agentresp.ChatResp

		if len(currentData) == 0 {
			chatlogrecord.LogFailedExecution(ctx, req, err, nil)
		} else {
			unmarshalErr := sonic.Unmarshal(currentData, &agentResp)
			if unmarshalErr != nil {
				chatlogrecord.LogFailedExecution(ctx, req, err, nil)
				agentSvc.logger.Errorf("[Process] unmarshal currentData err: %v", err)
			} else {
				chatlogrecord.LogFailedExecution(ctx, req, err, &agentResp)
			}
		}

		// NOTE: 上报运行失败日志
		// NOTE: 分类讨论
		if req.Stream {
			// NOTE: 如果err不为nil，则把err写入到respChan,是chatresponse结构，可以携带正确数据的信息
			StreamDiff(ctx, seq, lastData, currentData, respChan)
		} else {
			// NOTE: 非流式处理，直接返回err，直接是错误码，无法携带正确数据信息
			httpErr := rest.NewHTTPError(ctx, http.StatusInternalServerError, apierr.AgentAPP_InternalError).WithErrorDetails(err.Error())
			errBytes, _ := sonic.Marshal(httpErr)
			respChan <- errBytes
		}
	}

	if isEnd {
		session.CloseSignal()
		SessionMap.Delete(req.ConversationID)
		stopChanMap.Delete(req.ConversationID)
		progressMap.Delete(req.AssistantMessageID)
		progressSet.Delete(req.AssistantMessageID)
		
		isInterruptPreProgressGetMap.Delete(req.AssistantMessageID)

		if req.Stream {
			emitJSON(seq, respChan, []interface{}{}, nil, "end")
		}
	}
	// NOTE: 记录结束时间
	processTime := time.Since(startTime)
	// NOTE: 打印处理时间，ms
	agentSvc.logger.Infof("[Process] chat process time: %d ms", processTime.Milliseconds())

	return nil
}
