package agentsvc

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/stretchr/testify/assert"
)

func TestNewAgentSvc_WithMinimalDto(t *testing.T) {
	dto := &NewAgentSvcDto{
		SvcBase:             service.NewSvcBase(),
		StreamDiffFrequency: 100,
	}

	svc := NewAgentSvc(dto)

	assert.NotNil(t, svc)
}

func TestNewAgentSvc_WithNilDto_Panics(t *testing.T) {
	assert.Panics(t, func() {
		_ = NewAgentSvc(nil)
	})
}
