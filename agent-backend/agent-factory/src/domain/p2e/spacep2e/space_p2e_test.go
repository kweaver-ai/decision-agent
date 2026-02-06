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

func TestSpaces(t *testing.T) {
	ctx := context.Background()

	tests := []struct {
		name    string
		pos     []*dapo.SpacePo
		wantErr bool
		checkEOs func(t *testing.T, eos []*spaceeo.Space)
	}{
		{
			name: "multiple valid spaces",
			pos: []*dapo.SpacePo{
				{
					ID:   "space-1",
					Name: "Space 1",
					Key:  "space-1",
				},
				{
					ID:   "space-2",
					Name: "Space 2",
					Key:  "space-2",
				},
			},
			wantErr: false,
			checkEOs: func(t *testing.T, eos []*spaceeo.Space) {
				assert.Len(t, eos, 2)
				assert.Equal(t, "space-1", eos[0].ID)
				assert.Equal(t, "Space 1", eos[0].Name)
				assert.Equal(t, "space-2", eos[1].ID)
				assert.Equal(t, "Space 2", eos[1].Name)

				// Check that CreatedByName and UpdatedByName are set in local dev
				// The format should be "{userID}_name"
				assert.Contains(t, eos[0].CreatedByName, "_name")
				assert.Contains(t, eos[0].UpdatedByName, "_name")
			},
		},
		{
			name:    "empty slice",
			pos:     []*dapo.SpacePo{},
			wantErr: false,
			checkEOs: func(t *testing.T, eos []*spaceeo.Space) {
				assert.Len(t, eos, 0)
			},
		},
		{
			name:    "nil slice",
			pos:     nil,
			wantErr: false,
			checkEOs: func(t *testing.T, eos []*spaceeo.Space) {
				assert.Len(t, eos, 0)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			eos, err := Spaces(ctx, tt.pos, nil)
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				require.NoError(t, err)
				if tt.checkEOs != nil {
					tt.checkEOs(t, eos)
				}
			}
		})
	}
}
