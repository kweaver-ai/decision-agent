package personalspacesvc

import (
	"context"

	"github.com/kweaver-ai/agent-go-common-pkg/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/agent-go-common-pkg/src/domain/enum/cdapmsenum"
)

func (s *PersonalSpaceService) isHasBuiltInAgentMgmtPermission(ctx context.Context) (has bool, err error) {
	has, err = s.pmsSvc.GetSingleMgmtPermission(ctx, cdaenum.ResourceTypeDataAgent, cdapmsenum.AgentBuiltInAgentMgmt)
	return
}
