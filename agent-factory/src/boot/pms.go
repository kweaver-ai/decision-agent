package boot

import (
    "context"

    "devops.aishu.cn/AISHUDevOps/DIP/_git/agent-factory/src/domain/service/inject/v3/dainject"
    _ "github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/capierr"
    "github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper/cenvhelper"
)

func initPermission() (err error) {
    //if common.IsDisablePmsCheck() {
    //	return
    //}
    if cenvhelper.IsLocalDev(cenvhelper.RunScenario_Aaron_Local_Dev) {
        return
    }

    pmsSvc := dainject.NewPermissionSvc()
    ctx := context.Background()

    err = pmsSvc.InitPermission(ctx)
    if err != nil {
        return
    }

    return
}
