package chttpinject

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/authzhttp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iauthzacc"
	"github.com/kweaver-ai/kweaver-go-lib/logger"
)

var (
	authZOnce sync.Once
	authZImpl iauthzacc.AuthZHttpAcc
)

func NewAuthZHttpAcc() iauthzacc.AuthZHttpAcc {
	authZOnce.Do(func() {
		authZImpl = authzhttp.NewAuthZHttpAcc(
			logger.GetLogger(),
		)
	})

	return authZImpl
}
