package permissionsvc

import (
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdapmsenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iauthzacc/authzaccmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iumacc/httpaccmock"
	"github.com/stretchr/testify/assert"
)

func TestNewPermissionService_WithAllDependencies(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	dto := &NewPermissionSvcDto{
		SvcBase:               service.NewSvcBase(),
		AgentConfigRepo:       idbaccessmock.NewMockIDataAgentConfigRepo(ctrl),
		ReleaseRepo:           idbaccessmock.NewMockIReleaseRepo(ctrl),
		ReleasePermissionRepo:  idbaccessmock.NewMockIReleasePermissionRepo(ctrl),
		UmHttp:                httpaccmock.NewMockUmHttpAcc(ctrl),
		AuthZHttp:             authzaccmock.NewMockAuthZHttpAcc(ctrl),
		SpaceRepo:             idbaccessmock.NewMockISpaceRepo(ctrl),
	}

	svc := NewPermissionService(dto)

	assert.NotNil(t, svc)
	assert.IsType(t, &permissionSvc{}, svc)
}

func TestNewPermissionService_WithMinimalDependencies(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	dto := &NewPermissionSvcDto{
		SvcBase: service.NewSvcBase(),
		AgentConfigRepo:       nil,
		ReleaseRepo:           nil,
		ReleasePermissionRepo:  nil,
		UmHttp:                nil,
		AuthZHttp:             nil,
		SpaceRepo:             nil,
	}

	svc := NewPermissionService(dto)

	assert.NotNil(t, svc)
}

func TestBuildAgentOperationItem(t *testing.T) {
	tests := []struct {
		name           string
		op             cdapmsenum.Operator
		expectedNil    bool
		expectedID     string
		checkNames     bool
		checkScope     bool
		expectedScope  []string
	}{
		{
			name:          "AgentPublish operation",
			op:            cdapmsenum.AgentPublish,
			expectedNil:   false,
			expectedID:    string(cdapmsenum.AgentPublish),
			checkNames:    true,
			checkScope:    true,
			expectedScope: []string{"type"},
		},
		{
			name:          "AgentUnpublish operation",
			op:            cdapmsenum.AgentUnpublish,
			expectedNil:   false,
			expectedID:    string(cdapmsenum.AgentUnpublish),
			checkNames:    true,
			checkScope:    true,
			expectedScope: []string{"type"},
		},
		{
			name:          "AgentUse operation",
			op:            cdapmsenum.AgentUse,
			expectedNil:   false,
			expectedID:    string(cdapmsenum.AgentUse),
			checkNames:    true,
			checkScope:    true,
			expectedScope: []string{"type", "instance"},
		},
		{
			name:          "AgentCreateSystemAgent operation",
			op:            cdapmsenum.AgentCreateSystemAgent,
			expectedNil:   false,
			expectedID:    string(cdapmsenum.AgentCreateSystemAgent),
			checkNames:    true,
			checkScope:    true,
			expectedScope: []string{"type"},
		},
		{
			name:        "Unknown operation returns nil",
			op:          cdapmsenum.Operator("unknown_operation"),
			expectedNil: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := buildAgentOperationItem(tt.op)

			if tt.expectedNil {
				assert.Nil(t, result)
			} else {
				assert.NotNil(t, result)
				assert.Equal(t, tt.expectedID, result.ID)

				if tt.checkNames {
					assert.NotNil(t, result.Name)
					assert.Len(t, result.Name, 3) // Should have 3 language variants

					// Check that all required languages are present
					languages := make(map[string]bool)
					for _, name := range result.Name {
						languages[name.Language] = true
					}
					assert.True(t, languages["zh-cn"])
					assert.True(t, languages["en-us"])
					assert.True(t, languages["zh-tw"])
				}

				if tt.checkScope {
					assert.Equal(t, tt.expectedScope, result.Scope)
				}
			}
		})
	}
}

