package service

import (
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/cmp/icmp"
	"github.com/kweaver-ai/kweaver-go-lib/logger"
)

type SvcBase struct {
	logger icmp.Logger
}

func NewSvcBase() *SvcBase {
	return &SvcBase{
		logger: logger.GetLogger(),
	}
}
