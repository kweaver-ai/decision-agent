package iagentfactoryacc

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/agentfactoryhttp/afhttpdto"
)

//go:generate mockgen -source=./agent_factory.go -destination ./agent_factory_mock.go -package agent_factory_mock
type IAgentFactoryHttpAcc interface {
	CheckAgentUsePermission(ctx context.Context, req *afhttpdto.CheckPmsReq) (ok bool, err error)
}
