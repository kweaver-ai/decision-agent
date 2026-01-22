package srdbarg

import (
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/common"
)

type GetSRListArg struct {
	SpaceID      string
	PageByIntID  *common.PageByLastIntID
	ResourceType cdaenum.ResourceType
}

func NewGetSRListArg() *GetSRListArg {
	return &GetSRListArg{}
}
