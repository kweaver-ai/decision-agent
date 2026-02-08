package v3agentconfigsvc

import (
	"context"
	"errors"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdapmsenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driver/iv3portdriver/v3portdrivermock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestIsHasTplPublishPermission(t *testing.T) {
	tests := []struct {
		name    string
		setup   func(*gomock.Controller) (*dataAgentConfigSvc, context.Context)
		want    bool
		wantErr bool
	}{
		{
			name: "has template publish permission",
			setup: func(ctrl *gomock.Controller) (*dataAgentConfigSvc, context.Context) {
				ctx := context.Background()
				pmsSvc := v3portdrivermock.NewMockIPermissionSvc(ctrl)

				pmsSvc.EXPECT().
					GetSingleMgmtPermission(ctx, cdaenum.ResourceTypeDataAgentTpl, cdapmsenum.AgentTplPublish).
					Return(true, nil)

				svc := &dataAgentConfigSvc{
					SvcBase: service.NewSvcBase(),
					pmsSvc:  pmsSvc,
				}

				return svc, ctx
			},
			want:    true,
			wantErr: false,
		},
		{
			name: "no template publish permission",
			setup: func(ctrl *gomock.Controller) (*dataAgentConfigSvc, context.Context) {
				ctx := context.Background()
				pmsSvc := v3portdrivermock.NewMockIPermissionSvc(ctrl)

				pmsSvc.EXPECT().
					GetSingleMgmtPermission(ctx, cdaenum.ResourceTypeDataAgentTpl, cdapmsenum.AgentTplPublish).
					Return(false, nil)

				svc := &dataAgentConfigSvc{
					SvcBase: service.NewSvcBase(),
					pmsSvc:  pmsSvc,
				}

				return svc, ctx
			},
			want:    false,
			wantErr: false,
		},
		{
			name: "permission service error",
			setup: func(ctrl *gomock.Controller) (*dataAgentConfigSvc, context.Context) {
				ctx := context.Background()
				pmsSvc := v3portdrivermock.NewMockIPermissionSvc(ctrl)

				pmsSvc.EXPECT().
					GetSingleMgmtPermission(ctx, cdaenum.ResourceTypeDataAgentTpl, cdapmsenum.AgentTplPublish).
					Return(false, errors.New("permission error"))

				svc := &dataAgentConfigSvc{
					SvcBase: service.NewSvcBase(),
					pmsSvc:  pmsSvc,
				}

				return svc, ctx
			},
			want:    false,
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			defer ctrl.Finish()

			svc, ctx := tt.setup(ctrl)
			result, err := svc.isHasTplPublishPermission(ctx)

			if tt.wantErr {
				assert.Error(t, err)
			} else {
				require.NoError(t, err)
				assert.Equal(t, tt.want, result)
			}
		})
	}
}

func TestIsHasBuiltInAgentMgmtPermission(t *testing.T) {
	tests := []struct {
		name    string
		setup   func(*gomock.Controller) (*dataAgentConfigSvc, context.Context)
		want    bool
		wantErr bool
	}{
		{
			name: "has built-in agent mgmt permission",
			setup: func(ctrl *gomock.Controller) (*dataAgentConfigSvc, context.Context) {
				ctx := context.Background()
				pmsSvc := v3portdrivermock.NewMockIPermissionSvc(ctrl)

				pmsSvc.EXPECT().
					GetSingleMgmtPermission(ctx, cdaenum.ResourceTypeDataAgent, cdapmsenum.AgentBuiltInAgentMgmt).
					Return(true, nil)

				svc := &dataAgentConfigSvc{
					SvcBase: service.NewSvcBase(),
					pmsSvc:  pmsSvc,
				}

				return svc, ctx
			},
			want:    true,
			wantErr: false,
		},
		{
			name: "no built-in agent mgmt permission",
			setup: func(ctrl *gomock.Controller) (*dataAgentConfigSvc, context.Context) {
				ctx := context.Background()
				pmsSvc := v3portdrivermock.NewMockIPermissionSvc(ctrl)

				pmsSvc.EXPECT().
					GetSingleMgmtPermission(ctx, cdaenum.ResourceTypeDataAgent, cdapmsenum.AgentBuiltInAgentMgmt).
					Return(false, nil)

				svc := &dataAgentConfigSvc{
					SvcBase: service.NewSvcBase(),
					pmsSvc:  pmsSvc,
				}

				return svc, ctx
			},
			want:    false,
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			defer ctrl.Finish()

			svc, ctx := tt.setup(ctrl)
			result, err := svc.isHasBuiltInAgentMgmtPermission(ctx)

			if tt.wantErr {
				assert.Error(t, err)
			} else {
				require.NoError(t, err)
				assert.Equal(t, tt.want, result)
			}
		})
	}
}

func TestIsHasSystemAgentCreatePermission(t *testing.T) {
	tests := []struct {
		name    string
		setup   func(*gomock.Controller) (*dataAgentConfigSvc, context.Context)
		want    bool
		wantErr bool
	}{
		{
			name: "has system agent create permission",
			setup: func(ctrl *gomock.Controller) (*dataAgentConfigSvc, context.Context) {
				ctx := context.Background()
				pmsSvc := v3portdrivermock.NewMockIPermissionSvc(ctrl)

				pmsSvc.EXPECT().
					GetSingleMgmtPermission(ctx, cdaenum.ResourceTypeDataAgent, cdapmsenum.AgentCreateSystemAgent).
					Return(true, nil)

				svc := &dataAgentConfigSvc{
					SvcBase: service.NewSvcBase(),
					pmsSvc:  pmsSvc,
				}

				return svc, ctx
			},
			want:    true,
			wantErr: false,
		},
		{
			name: "no system agent create permission",
			setup: func(ctrl *gomock.Controller) (*dataAgentConfigSvc, context.Context) {
				ctx := context.Background()
				pmsSvc := v3portdrivermock.NewMockIPermissionSvc(ctrl)

				pmsSvc.EXPECT().
					GetSingleMgmtPermission(ctx, cdaenum.ResourceTypeDataAgent, cdapmsenum.AgentCreateSystemAgent).
					Return(false, nil)

				svc := &dataAgentConfigSvc{
					SvcBase: service.NewSvcBase(),
					pmsSvc:  pmsSvc,
				}

				return svc, ctx
			},
			want:    false,
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			defer ctrl.Finish()

			svc, ctx := tt.setup(ctrl)
			result, err := svc.isHasSystemAgentCreatePermission(ctx)

			if tt.wantErr {
				assert.Error(t, err)
			} else {
				require.NoError(t, err)
				assert.Equal(t, tt.want, result)
			}
		})
	}
}

func TestIsOwnerOrHasBuiltInAgentMgmtPermission(t *testing.T) {
	tests := []struct {
		name    string
		setup   func(*gomock.Controller) (*dataAgentConfigSvc, context.Context, *dapo.DataAgentPo)
		uid     string
		wantErr bool
	}{
		{
			name: "is owner - should pass",
			setup: func(ctrl *gomock.Controller) (*dataAgentConfigSvc, context.Context, *dapo.DataAgentPo) {
				ctx := context.Background()
				pmsSvc := v3portdrivermock.NewMockIPermissionSvc(ctrl)

				builtIn := cdaenum.BuiltInNo
				po := &dapo.DataAgentPo{
					CreatedBy: "user-123",
					IsBuiltIn: &builtIn,
				}

				svc := &dataAgentConfigSvc{
					SvcBase: service.NewSvcBase(),
					pmsSvc:  pmsSvc,
				}

				return svc, ctx, po
			},
			uid:     "user-123",
			wantErr: false,
		},
		{
			name: "not owner, not built-in - should error",
			setup: func(ctrl *gomock.Controller) (*dataAgentConfigSvc, context.Context, *dapo.DataAgentPo) {
				ctx := context.Background()
				pmsSvc := v3portdrivermock.NewMockIPermissionSvc(ctrl)

				builtIn := cdaenum.BuiltInNo
				po := &dapo.DataAgentPo{
					CreatedBy: "user-456",
					IsBuiltIn: &builtIn,
				}

				svc := &dataAgentConfigSvc{
					SvcBase: service.NewSvcBase(),
					pmsSvc:  pmsSvc,
				}

				return svc, ctx, po
			},
			uid:     "user-123",
			wantErr: true,
		},
		{
			name: "not owner, is built-in, has mgmt permission - should pass",
			setup: func(ctrl *gomock.Controller) (*dataAgentConfigSvc, context.Context, *dapo.DataAgentPo) {
				ctx := context.Background()
				pmsSvc := v3portdrivermock.NewMockIPermissionSvc(ctrl)

				builtIn := cdaenum.BuiltInYes
				po := &dapo.DataAgentPo{
					CreatedBy: "user-456",
					IsBuiltIn: &builtIn,
				}

				pmsSvc.EXPECT().
					GetSingleMgmtPermission(ctx, cdaenum.ResourceTypeDataAgent, cdapmsenum.AgentBuiltInAgentMgmt).
					Return(true, nil)

				svc := &dataAgentConfigSvc{
					SvcBase: service.NewSvcBase(),
					pmsSvc:  pmsSvc,
				}

				return svc, ctx, po
			},
			uid:     "user-123",
			wantErr: false,
		},
		{
			name: "not owner, is built-in, no mgmt permission - should error",
			setup: func(ctrl *gomock.Controller) (*dataAgentConfigSvc, context.Context, *dapo.DataAgentPo) {
				ctx := context.Background()
				pmsSvc := v3portdrivermock.NewMockIPermissionSvc(ctrl)

				builtIn := cdaenum.BuiltInYes
				po := &dapo.DataAgentPo{
					CreatedBy: "user-456",
					IsBuiltIn: &builtIn,
				}

				pmsSvc.EXPECT().
					GetSingleMgmtPermission(ctx, cdaenum.ResourceTypeDataAgent, cdapmsenum.AgentBuiltInAgentMgmt).
					Return(false, nil)

				svc := &dataAgentConfigSvc{
					SvcBase: service.NewSvcBase(),
					pmsSvc:  pmsSvc,
				}

				return svc, ctx, po
			},
			uid:     "user-123",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			defer ctrl.Finish()

			svc, ctx, po := tt.setup(ctrl)
			err := svc.isOwnerOrHasBuiltInAgentMgmtPermission(ctx, po, tt.uid)

			if tt.wantErr {
				assert.Error(t, err)
			} else {
				require.NoError(t, err)
			}
		})
	}
}
