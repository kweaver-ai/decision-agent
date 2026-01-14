// Package common dbPool
package common

import (
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/cenvhelper"
)

func IsDisablePmsCheck() bool {
	return cenvhelper.IsDisablePmsCheck()
}
