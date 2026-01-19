package tempareasvc

import (
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iagentfactoryhttp"
	iecoConfighttp "github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iecoconfighttp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iefasthttp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driver/iportdriver"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp"
)

type tempareaSvc struct {
	*service.SvcBase
	logger       icmp.Logger
	tempAreaRepo idbaccess.ITempAreaRepo
	agentFactory iagentfactoryhttp.IAgentFactory
	EcoConfig    iecoConfighttp.IEcoConfig
	Efast        iefasthttp.IEfast
}

var _ iportdriver.ITempAreaSvc = &tempareaSvc{}

type NewTempAreaSvcDto struct {
	SvcBase      *service.SvcBase
	Logger       icmp.Logger
	TempAreaRepo idbaccess.ITempAreaRepo
	AgentFactory iagentfactoryhttp.IAgentFactory
	EcoConfig    iecoConfighttp.IEcoConfig
	Efast        iefasthttp.IEfast
}

func NewTempAreaService(dto *NewTempAreaSvcDto) iportdriver.ITempAreaSvc {
	impl := &tempareaSvc{
		SvcBase:      dto.SvcBase,
		logger:       dto.Logger,
		tempAreaRepo: dto.TempAreaRepo,
		agentFactory: dto.AgentFactory,
		EcoConfig:    dto.EcoConfig,
		Efast:        dto.Efast,
	}

	return impl
}
