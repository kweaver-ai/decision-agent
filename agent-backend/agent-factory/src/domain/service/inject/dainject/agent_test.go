package dainject

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewAgentSvc_PanicsWithoutGlobalConfig(t *testing.T) {
	// The NewAgentSvc function requires global.GConfig to be initialized
	// In test environment without global config, it will panic
	assert.Panics(t, func() {
		_ = NewAgentSvc()
	})
}

