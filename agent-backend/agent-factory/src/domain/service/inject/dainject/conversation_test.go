package dainject

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewConversationSvc_SingletonAndConstruct(t *testing.T) {
	initInjectGlobalConfig(t)
	resetInjectSingletons()

	first := NewConversationSvc()
	second := NewConversationSvc()

	assert.NotNil(t, first)
	assert.Same(t, first, second)
}
