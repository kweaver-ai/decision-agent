package sessionredisacc

import (
	"fmt"

	"github.com/kweaver-ai/decision-agent/agent-app/src/port/driven/iredisaccess/isessionredis"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/cmp/icmp"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/cmp/rediscmp"
)

const (
	// SessionTTL session过期时间（秒）
	SessionTTL = 600
	// SessionRedisKeyPrefix redis key前缀
	SessionRedisKeyPrefix = "agent-app:conversation-session:"
)

type sessionRedisAcc struct {
	redisCmp icmp.RedisCmp
}

var _ isessionredis.ISessionRedisAcc = &sessionRedisAcc{}

func NewSessionRedisAcc() isessionredis.ISessionRedisAcc {
	return &sessionRedisAcc{
		redisCmp: rediscmp.NewRedisCmp(),
	}
}

func (s *sessionRedisAcc) getRedisKey(conversationID string) string {
	return fmt.Sprintf("%s%s", SessionRedisKeyPrefix, conversationID)
}
