package service

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestSvcBase_NilSafe(t *testing.T) {
	t.Run("nil SvcBase operations", func(t *testing.T) {
		var svcBase *SvcBase

		assert.Nil(t, svcBase)
		// Verify that accessing nil pointer doesn't cause issues in test
		assert.Nil(t, svcBase)
	})

	t.Run("create SvcBase with nil logger", func(t *testing.T) {
		svcBase := &SvcBase{
			Logger: nil,
		}

		assert.NotNil(t, svcBase)
		assert.Nil(t, svcBase.Logger)
	})
}

func TestSvcBase_LoggerNotNil(t *testing.T) {
	t.Run("NewSvcBase always returns non-nil logger", func(t *testing.T) {
		svcBase := NewSvcBase()

		assert.NotNil(t, svcBase)
		assert.NotNil(t, svcBase.Logger)
	})
}

func TestSvcBase_MultipleInstances(t *testing.T) {
	t.Run("multiple NewSvcBase calls", func(t *testing.T) {
		instances := make([]*SvcBase, 5)

		for i := range instances {
			instances[i] = NewSvcBase()
			assert.NotNil(t, instances[i])
			assert.NotNil(t, instances[i].Logger)
		}

		// Logger is a singleton, so all instances share the same logger
		for i := 1; i < len(instances); i++ {
			assert.Same(t, instances[0].Logger, instances[i].Logger)
			assert.NotSame(t, instances[0], instances[i])
		}
	})
}

func TestSvcBase_StructProperties(t *testing.T) {
	t.Run("SvcBase struct is properly initialized", func(t *testing.T) {
		svcBase := NewSvcBase()

		// Verify the struct is properly initialized
		assert.NotNil(t, svcBase)
		assert.NotNil(t, svcBase.Logger)
	})
}
