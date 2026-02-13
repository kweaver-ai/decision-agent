package dainject

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewObservabilitySvc_SingletonAndConstruct(t *testing.T) {
	initInjectGlobalConfig(t)
	resetInjectSingletons()

	first := NewObservabilitySvc()
	second := NewObservabilitySvc()

	assert.NotNil(t, first)
	assert.Same(t, first, second)
}
