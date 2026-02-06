package spacep2e

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/spaceeo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestSpace(t *testing.T) {
	ctx := context.Background()

	tests := []struct {
		name    string
		po      *dapo.SpacePo
		wantErr bool
		checkEO func(t *testing.T, eo *spaceeo.Space)
	}{
		{
			name: "valid space PO",
			po: &dapo.SpacePo{
				ID:          "space-1",
				Name:        "Test Space",
				Key:         "test-space",
				Profile:     "Test Description",
				CreatedBy:   "user-1",
				CreatedAt:   1234567890,
				UpdatedBy:   "user-2",
				UpdatedAt:   1234567891,
			},
			wantErr: false,
			checkEO: func(t *testing.T, eo *spaceeo.Space) {
				assert.Equal(t, "space-1", eo.ID)
				assert.Equal(t, "Test Space", eo.Name)
				assert.Equal(t, "test-space", eo.Key)
				assert.Equal(t, "Test Description", eo.Profile)
				assert.Equal(t, "user-1", eo.CreatedBy)
				assert.Equal(t, int64(1234567890), eo.CreatedAt)
			},
		},
		{
			name: "space PO with minimal fields",
			po: &dapo.SpacePo{
				ID:   "space-2",
				Name: "Minimal Space",
			},
			wantErr: false,
			checkEO: func(t *testing.T, eo *spaceeo.Space) {
				assert.Equal(t, "space-2", eo.ID)
				assert.Equal(t, "Minimal Space", eo.Name)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			eo, err := Space(ctx, tt.po)
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				require.NoError(t, err)
				if tt.checkEO != nil {
					tt.checkEO(t, eo)
				}
			}
		})
	}
}
