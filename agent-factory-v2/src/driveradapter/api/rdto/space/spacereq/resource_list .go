package spacereq

import "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/common"

// ResourceListReq 空间资源列表请求
type ResourceListReq struct {
	common.PageByLastIntID
	Name string `form:"name" json:"name"` // 资源名称过滤
}

// GetErrMsgMap 返回错误信息映射
func (r *ResourceListReq) GetErrMsgMap() map[string]string {
	return r.PageByLastIntID.GetErrMsgMap()
}
