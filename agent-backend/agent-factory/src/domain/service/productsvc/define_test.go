package productsvc

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewProductService(t *testing.T) {
	t.Run("creates singleton service instance", func(t *testing.T) {
		svc := NewProductService()

		assert.NotNil(t, svc)
		assert.IsType(t, &productSvc{}, svc)
	})

	t.Run("returns same instance on multiple calls", func(t *testing.T) {
		svc1 := NewProductService()
		svc2 := NewProductService()

		assert.Same(t, svc1, svc2)
	})
}
