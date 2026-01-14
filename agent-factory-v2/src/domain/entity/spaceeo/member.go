package spaceeo

import (
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
)

// SpaceMember 空间成员实体对象
type SpaceMember struct {
	dapo.SpaceMemberPo

	ObjName string `json:"obj_name"` // 组织对象名称
}
