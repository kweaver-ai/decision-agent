package agentsvc

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/stretchr/testify/assert"
)

func TestNewAgentSvc(t *testing.T) {
	t.Run("creates service with minimal dependencies", func(t *testing.T) {
		dto := &NewAgentSvcDto{
			SvcBase:             service.NewSvcBase(),
			StreamDiffFrequency: 5,
		}

		svc := NewAgentSvc(dto)

		assert.NotNil(t, svc)
		assert.IsType(t, &agentSvc{}, svc)
	})

	t.Run("creates service with zero stream diff frequency", func(t *testing.T) {
		dto := &NewAgentSvcDto{
			SvcBase:             service.NewSvcBase(),
			StreamDiffFrequency: 0,
		}

		svc := NewAgentSvc(dto)

		assert.NotNil(t, svc)
		assert.IsType(t, &agentSvc{}, svc)
	})

	t.Run("creates service with negative stream diff frequency", func(t *testing.T) {
		dto := &NewAgentSvcDto{
			SvcBase:             service.NewSvcBase(),
			StreamDiffFrequency: -1,
		}

		svc := NewAgentSvc(dto)

		assert.NotNil(t, svc)
		assert.IsType(t, &agentSvc{}, svc)
	})
}
