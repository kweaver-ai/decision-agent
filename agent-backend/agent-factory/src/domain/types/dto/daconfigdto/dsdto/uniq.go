package dsdto

import "github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/comvalobj"

type DsUniqDto = comvalobj.DataAgentUniqFlag

func NewDsIndexUniqDto(agentID, agentVersion string) *DsUniqDto {
	return &DsUniqDto{
		AgentID:      agentID,
		AgentVersion: agentVersion,
	}
}
