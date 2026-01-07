package iagentfactoryhttp

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-app/src/drivenadapter/httpaccess/agentfactoryaccess/agentfactorydto"
)

type IAgentFactory interface {
	GetAgent(ctx context.Context, agentID string, version string) (agentfactorydto.Agent, error)
}
