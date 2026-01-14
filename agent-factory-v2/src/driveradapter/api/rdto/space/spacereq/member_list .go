package spacereq

import "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/common"

// MemberListReq member列表请求
type MemberListReq struct {
	common.PageByLastIntID
}

// GetErrMsgMap 返回错误信息映射
func (r *MemberListReq) GetErrMsgMap() map[string]string {
	return r.PageByLastIntID.GetErrMsgMap()
}
