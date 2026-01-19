package v2agentexecutordto

// V2AgentTerminateReq v2 版本的 Agent 终止执行请求
type V2AgentTerminateReq struct {
	AgentRunID string `json:"agent_run_id"` // Agent运行ID
}
