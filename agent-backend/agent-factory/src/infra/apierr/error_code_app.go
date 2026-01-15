package apierr

// APP 相关错误码 (来自 agent-app)
const (
	// 400
	AgentAPP_InvalidParameter_RequestBody = "AgentAPP.InvalidParameter.RequestBody"
	// 401
	AgentAPP_InvalidRequestHeader_Authorization = "AgentAPP.InvalidRequestHeader.Authorization"

	// 403
	AgentAPP_Forbidden_FilterField      = "AgentAPP.Forbidden.FilterField"
	AgentAPP_Forbidden_PermissionDenied = "AgentAPP.Forbidden.PermissionDenied"

	// 406
	AgentAPP_InvalidRequestHeader_ContentType = "AgentAPP.InvalidRequestHeader.ContentType"

	// 500
	AgentAPP_InternalError = "AgentAPP.InternalError"

	// Agent
	AgentAPP_Agent_GetAgentFailed           = "AgentAPP.Agent.GetAgentFailed"
	AgentAPP_Agent_CreateConversationFailed = "AgentAPP.Agent.CreateConversationFailed"
	AgentAPP_Agent_GetConversationFailed    = "AgentAPP.Agent.GetConversationFailed"
	AgentAPP_Agent_GetMaxIndexFailed        = "AgentAPP.Agent.GetMaxIndexFailed"
	AgentAPP_Agent_GetHistoryFailed         = "AgentAPP.Agent.GetHistoryFailed"
	AgentAPP_Agent_CreateMessageFailed      = "AgentAPP.Agent.CreateMessageFailed"
	AgentAPP_Agent_UpdateConversationFailed = "AgentAPP.Agent.UpdateConversationFailed"
	AgentAPP_Agent_GetMessageFailed         = "AgentAPP.Agent.GetMessageFailed"
	AgentAPP_Agent_UpdateMessageFailed      = "AgentAPP.Agent.UpdateMessageFailed"
	AgentAPP_Agent_CallAgentExecutorFailed  = "AgentAPP.Agent.CallAgentExecutorFailed"
	AgentAPP_Agent_ModelExecption           = "AgentAPP.Agent.ModelExecption"
	AgentAPP_Agent_SkillExecption           = "AgentAPP.Agent.SkillExecption"
	AgentAPP_Agent_DolphinSDKExecption      = "AgentAPP.Agent.DolphinSDKExecption"
	AgentAPP_Agent_ExecutorExecption        = "AgentAPP.Agent.ExecutorExecption"
	AgentAPP_Agent_ResumeFailed             = "AgentAPP.Agent.ResumeFailed"
	AgentAPP_Agent_SessionInitFailed        = "AgentAPP.Agent.ConversationSessionInitFailed"
)

// 会话相关错误码
const (
	ConversationNotFound      = "AgentAPP.Conversation.NotFound" // conversation 不存在
	ConversationDeleteFailed  = "AgentAPP.Conversation.DeleteFailed"
	ConversationDetailFailed  = "AgentAPP.Conversation.GetDetailFailed"
	ConversationInitFailed    = "AgentAPP.Conversation.InitFailed"
	ConversationGetListFailed = "AgentAPP.Conversation.GetListFailed"
)

const (
	TempAreaRemoveFailed = "AgentAPP.Temparea.RemoveFailed"
	TempAreaGetFailed    = "AgentAPP.Temparea.GetFailed"
	TempAreaCreateFailed = "AgentAPP.Temparea.Createfailed"
	TempAreaAppendFailed = "AgentAPP.Temparea.AppendFailed"
)
