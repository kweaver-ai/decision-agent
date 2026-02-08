package observabilitysvc

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewObservabilitySvc(t *testing.T) {
	dto := &NewObservabilitySvcDto{
		Logger:       nil,
		Uniquery:     nil,
		AgentFactory: nil,
	}

	svc := NewObservabilitySvc(dto)

	assert.NotNil(t, svc)
}
