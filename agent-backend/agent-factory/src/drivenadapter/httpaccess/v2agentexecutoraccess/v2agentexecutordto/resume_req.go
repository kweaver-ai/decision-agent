package v2agentexecutordto

// V2AgentResumeReq v2 版本的 Agent 恢复执行请求
type V2AgentResumeReq struct {
	AgentRunID string           `json:"agent_run_id"` // Agent运行ID
	ResumeInfo *V2AgentResumeInfo `json:"resume_info"`  // 恢复执行信息
}

// V2AgentResumeInfo 恢复执行信息
type V2AgentResumeInfo struct {
	ResumeHandle *V2ResumeHandle `json:"resume_handle"` // 恢复句柄
	Action       string          `json:"action"`        // 操作类型: confirm | skip
	ModifiedArgs []V2ModifiedArg `json:"modified_args"` // 修改后的参数
}

// V2ResumeHandle 恢复句柄
type V2ResumeHandle struct {
	FrameID       string `json:"frame_id"`       // 执行帧ID
	SnapshotID    string `json:"snapshot_id"`    // 快照ID
	ResumeToken   string `json:"resume_token"`   // 恢复令牌
	InterruptType string `json:"interrupt_type"` // 中断类型
	CurrentBlock  int    `json:"current_block"`  // 当前代码块索引
	RestartBlock  bool   `json:"restart_block"`  // 是否重启代码块
}

// V2ModifiedArg 修改后的参数
type V2ModifiedArg struct {
	Key   string      `json:"key"`   // 参数名称
	Value interface{} `json:"value"` // 参数值
}
