package agentsvc

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/conf"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp/cmpmock"
	"github.com/stretchr/testify/assert"
	"go.uber.org/mock/gomock"
)

func TestNewAgentSvc_WithMinimalDto(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockLogger := cmpmock.NewMockLogger(ctrl)

	dto := &NewAgentSvcDto{
		SvcBase:             service.NewSvcBase(),
		Logger:              mockLogger,
		StreamDiffFrequency: 100,
	}

	svc := NewAgentSvc(dto)
	concreteSvc, ok := svc.(*agentSvc)
	assert.True(t, ok, "NewAgentSvc should return *agentSvc concrete type")
	assert.NotNil(t, concreteSvc)
	assert.NotNil(t, concreteSvc.SvcBase)
	assert.Equal(t, 100, concreteSvc.streamDiffFrequency)
}

func TestNewAgentSvc_WithNilDto_Panics(t *testing.T) {
	assert.Panics(t, func() {
		_ = NewAgentSvc(nil)
	})
}

func TestNewAgentSvc_WithFullDto(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockLogger := cmpmock.NewMockLogger(ctrl)

	dto := &NewAgentSvcDto{
		SvcBase:             service.NewSvcBase(),
		Logger:              mockLogger,
		StreamDiffFrequency: 200,
		SandboxPlatformConf: &conf.SandboxPlatformConf{},
	}

	svc := NewAgentSvc(dto)
	concreteSvc, ok := svc.(*agentSvc)
	assert.True(t, ok, "NewAgentSvc should return *agentSvc concrete type")
	assert.NotNil(t, concreteSvc)
	assert.NotNil(t, concreteSvc.SvcBase)
	assert.Equal(t, 200, concreteSvc.streamDiffFrequency)
	assert.NotNil(t, concreteSvc.SessionMap)
	assert.NotNil(t, concreteSvc.progressMap)
	assert.NotNil(t, concreteSvc.progressSet)
}

func TestNewAgentSvc_SyncMapsInitialized(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockLogger := cmpmock.NewMockLogger(ctrl)

	dto := &NewAgentSvcDto{
		SvcBase:             service.NewSvcBase(),
		Logger:              mockLogger,
		StreamDiffFrequency: 50,
	}

	svc := NewAgentSvc(dto)
	concreteSvc, ok := svc.(*agentSvc)
	assert.True(t, ok)

	assert.NotNil(t, concreteSvc.SessionMap)
	assert.NotNil(t, concreteSvc.progressMap)
	assert.NotNil(t, concreteSvc.progressSet)

	// Test that sync.Map methods work
	concreteSvc.SessionMap.Store("test", "value")
	val, ok := concreteSvc.SessionMap.Load("test")
	assert.True(t, ok)
	assert.Equal(t, "value", val)
}

func TestAgentSvc_ImplementsInterface(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockLogger := cmpmock.NewMockLogger(ctrl)

	dto := &NewAgentSvcDto{
		SvcBase:             service.NewSvcBase(),
		Logger:              mockLogger,
		StreamDiffFrequency: 100,
	}

	svc := NewAgentSvc(dto)

	// Verify the type assertion at compile time
	var _ interface{} = svc
	assert.NotNil(t, svc)
}

func TestNewAgentSvcDto_DefaultValues(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockLogger := cmpmock.NewMockLogger(ctrl)

	dto := &NewAgentSvcDto{
		SvcBase:             service.NewSvcBase(),
		Logger:              mockLogger,
		StreamDiffFrequency: 0, // Default value
	}

	svc := NewAgentSvc(dto)
	concreteSvc, ok := svc.(*agentSvc)
	assert.True(t, ok)

	assert.NotNil(t, concreteSvc)
	assert.Equal(t, 0, concreteSvc.streamDiffFrequency)
}
