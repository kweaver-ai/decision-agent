package conf

import (
	"github.com/kweaver-ai/agent-go-common-pkg/cconf"
)

type AgentFactoryConf struct {
	PublicSvc  cconf.SvcConf `yaml:"public_svc"`
	PrivateSvc cconf.SvcConf `yaml:"private_svc"`
}
