package producte2p

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/producteo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestProduct(t *testing.T) {
	tests := []struct {
		name    string
		eo      *producteo.Product
		wantErr bool
		checkPO func(t *testing.T, po *dapo.ProductPo)
	}{
		{
			name: "valid product entity",
			eo: &producteo.Product{
				ProductPo: dapo.ProductPo{
					ID:      1,
					Name:    "Test Product",
					Key:     "test-product",
					Profile: "Test Description",
				},
			},
			wantErr: false,
			checkPO: func(t *testing.T, po *dapo.ProductPo) {
				assert.Equal(t, int64(1), po.ID)
				assert.Equal(t, "Test Product", po.Name)
				assert.Equal(t, "test-product", po.Key)
				assert.Equal(t, "Test Description", po.Profile)
			},
		},
		{
			name: "product with minimal fields",
			eo: &producteo.Product{
				ProductPo: dapo.ProductPo{
					ID:   2,
					Name: "Minimal Product",
				},
			},
			wantErr: false,
			checkPO: func(t *testing.T, po *dapo.ProductPo) {
				assert.Equal(t, int64(2), po.ID)
				assert.Equal(t, "Minimal Product", po.Name)
			},
		},
		{
			name:    "nil entity",
			eo:      nil,
			wantErr: false,
			checkPO: func(t *testing.T, po *dapo.ProductPo) {
				assert.Nil(t, po)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			po, err := Product(tt.eo)
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				require.NoError(t, err)
				if tt.checkPO != nil {
					tt.checkPO(t, po)
				}
			}
		})
	}
}
