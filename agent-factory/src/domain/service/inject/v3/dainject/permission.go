package dainject

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service/v3/permissionsvc"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/dbaccess/daconfdbacc"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/dbaccess/releaseacc"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/dbaccess/spacedb/spacedbacc"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driver/iv3portdriver"
	"github.com/kweaver-ai/agent-go-common-pkg/src/drivenadapter/httpaccess/chttpinject"
)

var (
	permissionSvcOnce sync.Once
	permissionSvcImpl iv3portdriver.IPermissionSvc
)

// NewPermissionSvc
func NewPermissionSvc() iv3portdriver.IPermissionSvc {
	permissionSvcOnce.Do(func() {
		dto := &permissionsvc.NewPermissionSvcDto{
			SvcBase:               service.NewSvcBase(),
			ReleaseRepo:           releaseacc.NewReleaseRepo(),
			ReleasePermissionRepo: releaseacc.NewReleasePermissionRepo(),
			AgentConfigRepo:       daconfdbacc.NewDataAgentRepo(),
			UmHttp:                chttpinject.NewUmHttpAcc(),
			AuthZHttp:             chttpinject.NewAuthZHttpAcc(),
			SpaceRepo:             spacedbacc.NewSpaceRepo(),
			// SpaceSvc:              NewCustomSpaceSvc(),
		}

		permissionSvcImpl = permissionsvc.NewPermissionService(dto)
	})

	return permissionSvcImpl
}
