package httpinject

import (
	"sync"

	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/drivenadapter/httpaccess/uniqueryaccess"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/infra/common/global"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/agent-app/src/port/driven/ihttpaccess/iuniqueryhttp"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/mdl-go-lib/logger"
	"devops.aishu.cn/AISHUDevOps/DIP/_git/mdl-go-lib/rest"
)

var (
	uniqueryOnce sync.Once
	uniqueryImpl iuniqueryhttp.IUniquery
)

func NewUniqueryHttpAcc() iuniqueryhttp.IUniquery {
	uniqueryOnce.Do(func() {
		uniqueryConf := global.GConfig.UniqueryConf
		uniqueryImpl = uniqueryaccess.NewUniqueryHttpAcc(
			logger.GetLogger(),
			uniqueryConf,
			rest.NewHTTPClient(),
		)
	})

	return uniqueryImpl
}
