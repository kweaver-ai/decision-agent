package spaceeo

import (
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/agentvo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
)

// SpaceResource 空间资源实体对象
type SpaceResource struct {
	dapo.SpaceResourcePo

	ResourceName string `json:"resource_name"` // 资源名称

	PublishedAgentInfo *agentvo.PublishedAgentInfo `json:"published_agent_info"` // 已发布智能体信息
}

func NewSpaceResource() *SpaceResource {
	return &SpaceResource{
		PublishedAgentInfo: agentvo.NewPublishedAgentInfo(),
	}
}
