package observabilitysvc

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewObservabilitySvc(t *testing.T) {
	t.Run("creates service with all dependencies", func(t *testing.T) {
		dto := &NewObservabilitySvcDto{
			Logger:       nil,
			Uniquery:     nil,
			AgentFactory: nil,
		}

		svc := NewObservabilitySvc(dto)

		assert.NotNil(t, svc)
		assert.IsType(t, &observabilitySvc{}, svc)
	})

	t.Run("creates service with minimal dependencies", func(t *testing.T) {
		dto := &NewObservabilitySvcDto{
			Logger:       nil,
			Uniquery:     nil,
			AgentFactory: nil,
		}

		svc := NewObservabilitySvc(dto)

		assert.NotNil(t, svc)
	})
}
