package agentreq

// ResumeReq 恢复聊天请求
type ResumeReq struct {
	ConversationID      string               `json:"conversation_id" binding:"required"` // 会话ID
	AgentRunID          string               `json:"agent_run_id"`                       // Agent运行ID（中断恢复时必填）
	ResumeInterruptInfo *ResumeInterruptInfo `json:"resume_interrupt_info"`              // 中断恢复信息（为nil时走原逻辑）
}

// ResumeInterruptInfo 中断恢复信息
type ResumeInterruptInfo struct {
	ResumeHandle *ResumeHandle `json:"resume_handle" binding:"required"` // 恢复句柄
	Action       string        `json:"action" binding:"required"`        // 操作类型: confirm | skip
	ModifiedArgs []ModifiedArg `json:"modified_args"`                    // 修改后的参数
}

// ResumeHandle 恢复句柄
type ResumeHandle struct {
	FrameID       string `json:"frame_id"`       // 执行帧ID
	SnapshotID    string `json:"snapshot_id"`    // 快照ID
	ResumeToken   string `json:"resume_token"`   // 恢复令牌
	InterruptType string `json:"interrupt_type"` // 中断类型
	CurrentBlock  int    `json:"current_block"`  // 当前代码块索引
	RestartBlock  bool   `json:"restart_block"`  // 是否重启代码块
}

// ModifiedArg 修改后的参数
type ModifiedArg struct {
	Key   string      `json:"key"`   // 参数名称
	Value interface{} `json:"value"` // 参数值
}
