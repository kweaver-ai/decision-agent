package sessionredisacc

import (
	"fmt"

	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driven/iredisaccess/isessionredis"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/cmp/icmp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/cmp/rediscmp"
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
