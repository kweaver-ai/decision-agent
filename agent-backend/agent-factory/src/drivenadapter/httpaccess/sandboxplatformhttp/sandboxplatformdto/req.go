package sandboxplatformdto

// CreateSessionReq 创建 Session 请求
type CreateSessionReq struct {
	UserID           string                 `json:"user_id"`
	AgentID          string                 `json:"agent_id"`
	BusinessDomainID string                 `json:"business_domain_id"`
	Config           map[string]interface{} `json:"config,omitempty"`
}
