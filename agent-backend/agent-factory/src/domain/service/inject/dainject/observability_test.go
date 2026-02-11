package dainject

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewObservabilitySvc_PanicsWithoutDependencies(t *testing.T) {
	// Note: This will panic in test environment without proper setup
	assert.Panics(t, func() {
		_ = NewObservabilitySvc()
	})
}
