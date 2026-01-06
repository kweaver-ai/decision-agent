package dsdto

import "github.com/kweaver-ai/agent-go-common-pkg/src/domain/valueobject/daconfvalobj"

// DsComDto ds common dto
type DsComDto struct {
	*DsUniqDto
	Config *daconfvalobj.Config
}

func NewDsComDto(agentID, agentVersion string, config *daconfvalobj.Config) *DsComDto {
	return &DsComDto{
		DsUniqDto: &DsUniqDto{
			AgentID:      agentID,
			AgentVersion: agentVersion,
		},
		Config: config,
	}
}
