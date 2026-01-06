// Package common dbPool
package common

import (
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper/cenvhelper"
)

func IsDisablePmsCheck() bool {
	return cenvhelper.IsDisablePmsCheck()
}
