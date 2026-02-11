package v3agentconfigsvc

import (
	"context"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/daconfeo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/daconfvalobj"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/daconfvalobj/skillvalobj"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
)

func TestDataAgentConfigSvc_DetailPmsCheck_PrivateAPI(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	svc := &dataAgentConfigSvc{
		SvcBase: service.NewSvcBase(),
	}

	ctx := context.Background()
	po := &dapo.DataAgentPo{
		ID:         "agent-1",
		Name:       "Test Agent",
		CreatedBy:  "user-123",
	}

	err := svc.detailPmsCheck(ctx, po, true, "user-456")

	assert.NoError(t, err)
}

func TestDataAgentConfigSvc_DetailPmsCheck_PublicAPI_NoPermission(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	svc := &dataAgentConfigSvc{
		SvcBase: service.NewSvcBase(),
	}

	ctx := context.Background()
	po := &dapo.DataAgentPo{
		ID:         "agent-1",
		Name:       "Test Agent",
		CreatedBy:  "user-123",
	}

	// isOwnerOrHasBuiltInAgentMgmtPermission will return error when user doesn't have permission
	err := svc.detailPmsCheck(ctx, po, false, "user-456")

	// This will fail with error since the user is not the owner and doesn't have built-in agent mgmt permission
	assert.Error(t, err)
}

func TestDataAgentConfigSvc_MarkSkillAgentPmsForDetail_NilSkill(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	svc := &dataAgentConfigSvc{
		SvcBase: service.NewSvcBase(),
	}

	ctx := context.Background()
	config := &daconfvalobj.Config{
		Skill: &skillvalobj.Skill{},
	}
	eo := &daconfeo.DataAgent{
		Config: config,
	}

	err := svc.markSkillAgentPmsForDetail(ctx, eo, "user-123")

	assert.NoError(t, err)
}

func TestDataAgentConfigSvc_MarkSkillAgentPmsForDetail_EmptySkillAgents(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	svc := &dataAgentConfigSvc{
		SvcBase: service.NewSvcBase(),
	}

	ctx := context.Background()
	config := &daconfvalobj.Config{
		Skill: &skillvalobj.Skill{
			Agents: []*skillvalobj.SkillAgent{},
		},
	}
	eo := &daconfeo.DataAgent{
		Config: config,
	}

	err := svc.markSkillAgentPmsForDetail(ctx, eo, "user-123")

	assert.NoError(t, err)
}

func TestDataAgentConfigSvc_DetailPmsCheck_SameUser(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	svc := &dataAgentConfigSvc{
		SvcBase: service.NewSvcBase(),
	}

	ctx := context.Background()
	po := &dapo.DataAgentPo{
		ID:         "agent-1",
		Name:       "Test Agent",
		CreatedBy:  "user-123",
	}

	err := svc.detailPmsCheck(ctx, po, false, "user-123")

	assert.NoError(t, err)
}
