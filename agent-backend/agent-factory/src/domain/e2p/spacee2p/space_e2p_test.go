package spacee2p

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/spaceeo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestSpace(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name    string
		eo      *spaceeo.Space
		wantErr bool
		checkPO func(t *testing.T, po *dapo.SpacePo)
	}{
		{
			name: "valid space entity",
			eo: &spaceeo.Space{
				SpacePo: dapo.SpacePo{
					ID:      "space-1",
					Name:    "Test Space",
					Profile: "Test Description",
				},
			},
			wantErr: false,
			checkPO: func(t *testing.T, po *dapo.SpacePo) {
				assert.Equal(t, "space-1", po.ID)
				assert.Equal(t, "Test Space", po.Name)
				assert.Equal(t, "Test Description", po.Profile)
			},
		},
		{
			name: "space with minimal fields",
			eo: &spaceeo.Space{
				SpacePo: dapo.SpacePo{
					ID:   "space-2",
					Name: "Minimal Space",
				},
			},
			wantErr: false,
			checkPO: func(t *testing.T, po *dapo.SpacePo) {
				assert.Equal(t, "space-2", po.ID)
				assert.Equal(t, "Minimal Space", po.Name)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()

			po, err := Space(tt.eo)
			if tt.wantErr {
				assert.Error(t, err)
				assert.Nil(t, po)
			} else {
				require.NoError(t, err)
				require.NotNil(t, po)

				if tt.checkPO != nil {
					tt.checkPO(t, po)
				}
			}
		})
	}
}

func TestSpaces(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name     string
		eos      []*spaceeo.Space
		wantErr  bool
		checkPOs func(t *testing.T, pos []*dapo.SpacePo)
	}{
		{
			name: "multiple valid spaces",
			eos: []*spaceeo.Space{
				{
					SpacePo: dapo.SpacePo{
						ID:   "space-1",
						Name: "Space 1",
					},
				},
				{
					SpacePo: dapo.SpacePo{
						ID:   "space-2",
						Name: "Space 2",
					},
				},
			},
			wantErr: false,
			checkPOs: func(t *testing.T, pos []*dapo.SpacePo) {
				assert.Len(t, pos, 2)
				assert.Equal(t, "space-1", pos[0].ID)
				assert.Equal(t, "space-2", pos[1].ID)
			},
		},
		{
			name:    "empty slice",
			eos:     []*spaceeo.Space{},
			wantErr: false,
			checkPOs: func(t *testing.T, pos []*dapo.SpacePo) {
				assert.Len(t, pos, 0)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()

			pos, err := Spaces(tt.eos)
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				require.NoError(t, err)

				if tt.checkPOs != nil {
					tt.checkPOs(t, pos)
				}
			}
		})
	}
}
