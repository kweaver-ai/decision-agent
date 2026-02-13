package dainject

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestV3Inject_Constructors(t *testing.T) {
	initV3InjectGlobalConfig(t)
	resetV3InjectSingletons()

	t.Run("NewBizDomainSvc", func(t *testing.T) {
		first := NewBizDomainSvc()
		second := NewBizDomainSvc()
		assert.NotNil(t, first)
		assert.Same(t, first, second)
	})

	t.Run("NewPermissionSvc", func(t *testing.T) {
		first := NewPermissionSvc()
		second := NewPermissionSvc()
		assert.NotNil(t, first)
		assert.Same(t, first, second)
	})

	t.Run("NewPublishedSvc", func(t *testing.T) {
		first := NewPublishedSvc()
		second := NewPublishedSvc()
		assert.NotNil(t, first)
		assert.Same(t, first, second)
	})

	t.Run("NewReleaseSvc", func(t *testing.T) {
		first := NewReleaseSvc()
		second := NewReleaseSvc()
		assert.NotNil(t, first)
		assert.Same(t, first, second)
	})

	t.Run("NewPersonalSpaceSvc", func(t *testing.T) {
		first := NewPersonalSpaceSvc()
		second := NewPersonalSpaceSvc()
		assert.NotNil(t, first)
		assert.Same(t, first, second)
	})

	t.Run("NewDaTplSvc", func(t *testing.T) {
		first := NewDaTplSvc()
		second := NewDaTplSvc()
		assert.NotNil(t, first)
		assert.Same(t, first, second)
	})

	t.Run("NewAgentInOutSvc", func(t *testing.T) {
		first := NewAgentInOutSvc()
		second := NewAgentInOutSvc()
		assert.NotNil(t, first)
		assert.Same(t, first, second)
	})
}
