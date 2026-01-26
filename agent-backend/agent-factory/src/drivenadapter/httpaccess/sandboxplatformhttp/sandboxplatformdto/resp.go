package sandboxplatformdto

// CreateSessionResp 创建 Session 响应
type CreateSessionResp struct {
	SessionID string                 `json:"session_id"`
	Status    string                 `json:"status"`
	CreatedAt int64                  `json:"created_at"`
	TTL       int64                  `json:"ttl"`
	Info      map[string]interface{} `json:"info,omitempty"`
}

// GetSessionResp 获取 Session 响应
type GetSessionResp struct {
	SessionID string `json:"session_id"`
	Status    string `json:"status"` // pending/running/stopped
	CreatedAt int64  `json:"created_at"`
	TTL       int64  `json:"ttl"`
}
