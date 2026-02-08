package agentinoutsvc

import (
	"context"
	"errors"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdapmsenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent_inout/agentinoutresp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driver/iv3portdriver/v3portdrivermock"
	"github.com/stretchr/testify/assert"
)

func TestCheckSystemAgentCreatePermission_NoSystemAgents(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockPmsSvc := v3portdrivermock.NewMockIPermissionSvc(ctrl)

	// Non-system agent
	isSystemAgent := cenum.YesNoInt8No
	exportData := &agentinoutresp.ExportResp{
		Agents: []*agentinoutresp.ExportAgentItem{
			{
				DataAgentPo: &dapo.DataAgentPo{
					Key:           "agent-1",
					Name:          "Regular Agent",
					IsSystemAgent: &isSystemAgent,
				},
			},
		},
	}
	resp := agentinoutresp.NewImportResp()

	svc := &agentInOutSvc{
		SvcBase: service.NewSvcBase(),
		pmsSvc:  mockPmsSvc,
	}

	ctx := context.Background()
	err := svc.checkSystemAgentCreatePermission(ctx, exportData, resp)

	assert.NoError(t, err)
	assert.Empty(t, resp.NoCreateSystemAgentPms)
}

func TestCheckSystemAgentCreatePermission_HasPermission(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockPmsSvc := v3portdrivermock.NewMockIPermissionSvc(ctrl)

	// System agent
	isSystemAgent := cenum.YesNoInt8Yes
	exportData := &agentinoutresp.ExportResp{
		Agents: []*agentinoutresp.ExportAgentItem{
			{
				DataAgentPo: &dapo.DataAgentPo{
					Key:           "sys-agent-1",
					Name:          "System Agent",
					IsSystemAgent: &isSystemAgent,
				},
			},
		},
	}
	resp := agentinoutresp.NewImportResp()

	mockPmsSvc.EXPECT().GetSingleMgmtPermission(gomock.Any(), cdaenum.ResourceTypeDataAgent, cdapmsenum.AgentCreateSystemAgent).Return(true, nil)

	svc := &agentInOutSvc{
		SvcBase: service.NewSvcBase(),
		pmsSvc:  mockPmsSvc,
	}

	ctx := context.Background()
	err := svc.checkSystemAgentCreatePermission(ctx, exportData, resp)

	assert.NoError(t, err)
	assert.Empty(t, resp.NoCreateSystemAgentPms)
}

func TestCheckSystemAgentCreatePermission_NoPermission(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockPmsSvc := v3portdrivermock.NewMockIPermissionSvc(ctrl)

	// System agent
	isSystemAgent := cenum.YesNoInt8Yes
	exportData := &agentinoutresp.ExportResp{
		Agents: []*agentinoutresp.ExportAgentItem{
			{
				DataAgentPo: &dapo.DataAgentPo{
					Key:           "sys-agent-1",
					Name:          "System Agent",
					IsSystemAgent: &isSystemAgent,
				},
			},
		},
	}
	resp := agentinoutresp.NewImportResp()

	mockPmsSvc.EXPECT().GetSingleMgmtPermission(gomock.Any(), cdaenum.ResourceTypeDataAgent, cdapmsenum.AgentCreateSystemAgent).Return(false, nil)

	svc := &agentInOutSvc{
		SvcBase: service.NewSvcBase(),
		pmsSvc:  mockPmsSvc,
	}

	ctx := context.Background()
	err := svc.checkSystemAgentCreatePermission(ctx, exportData, resp)

	assert.NoError(t, err)
	assert.NotEmpty(t, resp.NoCreateSystemAgentPms)
	assert.Len(t, resp.NoCreateSystemAgentPms, 1)
}

func TestCheckSystemAgentCreatePermission_PermissionError(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockPmsSvc := v3portdrivermock.NewMockIPermissionSvc(ctrl)

	// System agent
	isSystemAgent := cenum.YesNoInt8Yes
	exportData := &agentinoutresp.ExportResp{
		Agents: []*agentinoutresp.ExportAgentItem{
			{
				DataAgentPo: &dapo.DataAgentPo{
					Key:           "sys-agent-1",
					Name:          "System Agent",
					IsSystemAgent: &isSystemAgent,
				},
			},
		},
	}
	resp := agentinoutresp.NewImportResp()

	expectedErr := errors.New("permission error")
	mockPmsSvc.EXPECT().GetSingleMgmtPermission(gomock.Any(), cdaenum.ResourceTypeDataAgent, cdapmsenum.AgentCreateSystemAgent).Return(false, expectedErr)

	svc := &agentInOutSvc{
		SvcBase: service.NewSvcBase(),
		pmsSvc:  mockPmsSvc,
	}

	ctx := context.Background()
	err := svc.checkSystemAgentCreatePermission(ctx, exportData, resp)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "check system agent create permission failed")
}

func TestCheckSystemAgentCreatePermission_MultipleSystemAgents(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockPmsSvc := v3portdrivermock.NewMockIPermissionSvc(ctrl)

	// Multiple system agents
	isSystemAgent := cenum.YesNoInt8Yes
	exportData := &agentinoutresp.ExportResp{
		Agents: []*agentinoutresp.ExportAgentItem{
			{
				DataAgentPo: &dapo.DataAgentPo{
					Key:           "sys-agent-1",
					Name:          "System Agent 1",
					IsSystemAgent: &isSystemAgent,
				},
			},
			{
				DataAgentPo: &dapo.DataAgentPo{
					Key:           "sys-agent-2",
					Name:          "System Agent 2",
					IsSystemAgent: &isSystemAgent,
				},
			},
		},
	}
	resp := agentinoutresp.NewImportResp()

	mockPmsSvc.EXPECT().GetSingleMgmtPermission(gomock.Any(), cdaenum.ResourceTypeDataAgent, cdapmsenum.AgentCreateSystemAgent).Return(false, nil)

	svc := &agentInOutSvc{
		SvcBase: service.NewSvcBase(),
		pmsSvc:  mockPmsSvc,
	}

	ctx := context.Background()
	err := svc.checkSystemAgentCreatePermission(ctx, exportData, resp)

	assert.NoError(t, err)
	assert.NotEmpty(t, resp.NoCreateSystemAgentPms)
	assert.Len(t, resp.NoCreateSystemAgentPms, 2)
}

func TestCheckAgentConfigValid_EmptyAgents(t *testing.T) {
	svc := &agentInOutSvc{
		SvcBase: service.NewSvcBase(),
	}

	exportData := &agentinoutresp.ExportResp{
		Agents: []*agentinoutresp.ExportAgentItem{},
	}
	resp := agentinoutresp.NewImportResp()

	ctx := context.Background()
	svc.checkAgentConfigValid(ctx, exportData, resp)

	assert.False(t, resp.HasFail())
	assert.Empty(t, resp.ConfigInvalid)
}
