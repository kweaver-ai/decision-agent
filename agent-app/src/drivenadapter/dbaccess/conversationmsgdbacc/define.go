package conversationmsgdbacc

import (
	"sync"

	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-go-common-pkg/src/infra/cmp/icmp"
	"github.com/data-agent/agent-app/src/drivenadapter/dbaccess"
	"github.com/data-agent/agent-app/src/infra/common/global"
	"github.com/data-agent/agent-app/src/port/driven/idbaccess"
	"github.com/kweaver-ai/kweaver-go-lib/logger"

	"github.com/kweaver-ai/proton-rds-sdk-go/sqlx"
)

var (
	conversationMsgRepoOnce sync.Once
	conversationMsgRepoImpl idbaccess.IConversationMsgRepo
)

type ConversationMsgRepo struct {
	idbaccess.IDBAccBaseRepo

	db *sqlx.DB

	logger icmp.Logger
}

var _ idbaccess.IConversationMsgRepo = &ConversationMsgRepo{}

func NewConversationMsgRepo() idbaccess.IConversationMsgRepo {
	conversationMsgRepoOnce.Do(func() {
		conversationMsgRepoImpl = &ConversationMsgRepo{
			db:             global.GDB,
			logger:         logger.GetLogger(),
			IDBAccBaseRepo: dbaccess.NewDBAccBase(),
		}
	})

	return conversationMsgRepoImpl
}
