package productsvc

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewProductService(t *testing.T) {
	svc := NewProductService()

	assert.NotNil(t, svc)
}
