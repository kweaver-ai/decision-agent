package dainject

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestSingletonInjectorPattern(t *testing.T) {
	t.Run("NewConversationSvc panics without dependencies", func(t *testing.T) {
		// Note: These will panic in test environment without proper setup
		assert.Panics(t, func() {
			_ = NewConversationSvc()
		})
	})

	t.Run("NewSessionSvc returns non-nil in test environment", func(t *testing.T) {
		// SessionSvc might work in test environment
		svc := NewSessionSvc()
		assert.NotNil(t, svc)
	})
}
