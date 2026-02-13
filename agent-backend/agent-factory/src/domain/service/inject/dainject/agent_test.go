package dainject

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewAgentSvc_SingletonAndConstruct(t *testing.T) {
	initInjectGlobalConfig(t)
	resetInjectSingletons()

	first := NewAgentSvc()
	second := NewAgentSvc()

	assert.NotNil(t, first)
	assert.Same(t, first, second)
}
