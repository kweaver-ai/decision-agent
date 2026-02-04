package iagentfactoryacc

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/agentfactoryhttp/afhttpdto"
)

//go:generate mockgen -package agentfactorymock -destination ./agentfactorymock/agent_factory.go github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iagentfactoryacc IAgentFactoryHttpAcc
type IAgentFactoryHttpAcc interface {
	CheckAgentUsePermission(ctx context.Context, req *afhttpdto.CheckPmsReq) (ok bool, err error)
}
