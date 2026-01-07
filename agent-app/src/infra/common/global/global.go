package global

import (
	"github.com/kweaver-ai/decision-agent/agent-app/conf"

	"github.com/kweaver-ai/proton-rds-sdk-go/sqlx"
)

var (
	GConfig *conf.Config // 全局配置
	GDB     *sqlx.DB     // 全局 DB
)
