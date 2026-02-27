package spaceeo

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
)

func TestSpace_GetObjName(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name string
		s    *Space
		want string
	}{
		{
			name: "space with name",
			s: &Space{
				SpacePo: dapo.SpacePo{
					Name: "Test Space",
				},
			},
			want: "Test Space",
		},
		{
			name: "space with empty name",
			s: &Space{
				SpacePo: dapo.SpacePo{
					Name: "",
				},
			},
			want: "",
		},
		{
			name: "space with special characters",
			s: &Space{
				SpacePo: dapo.SpacePo{
					Name: "测试空间-123",
				},
			},
			want: "测试空间-123",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()

			got := tt.s.GetObjName()
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestSpace_AuditMngLogCreate(t *testing.T) {
	t.Parallel()

	s := &Space{
		SpacePo: dapo.SpacePo{
			ID:   "space-1",
			Name: "Test Space",
		},
	}

	// This should not panic
	assert.NotPanics(t, func() {
		s.AuditMngLogCreate(context.Background())
	})
}

func TestSpace_AuditMngLogUpdate(t *testing.T) {
	t.Parallel()

	s := &Space{
		SpacePo: dapo.SpacePo{
			ID:   "space-1",
			Name: "Test Space",
		},
	}

	// This should not panic
	assert.NotPanics(t, func() {
		s.AuditMngLogUpdate(context.Background())
	})
}

func TestSpace_AuditMngLogDelete(t *testing.T) {
	t.Parallel()

	s := &Space{
		SpacePo: dapo.SpacePo{
			ID:   "space-1",
			Name: "Test Space",
		},
	}

	// This should not panic
	assert.NotPanics(t, func() {
		s.AuditMngLogDelete(context.Background())
	})
}

func TestSpace_CreatedByName(t *testing.T) {
	t.Parallel()

	s := &Space{
		SpacePo: dapo.SpacePo{
			ID:   "space-1",
			Name: "Test Space",
		},
		CreatedByName: "Admin User",
	}

	assert.Equal(t, "Admin User", s.CreatedByName)
	assert.Equal(t, "", s.UpdatedByName)
}

func TestSpace_UpdatedByName(t *testing.T) {
	t.Parallel()

	s := &Space{
		SpacePo: dapo.SpacePo{
			ID:   "space-1",
			Name: "Test Space",
		},
		UpdatedByName: "Editor User",
	}

	assert.Equal(t, "Editor User", s.UpdatedByName)
	assert.Equal(t, "", s.CreatedByName)
}

func TestNewSpaceResource(t *testing.T) {
	t.Parallel()

	resource := NewSpaceResource()

	assert.NotNil(t, resource)
	assert.NotNil(t, resource.PublishedAgentInfo)
	assert.Empty(t, resource.ResourceName)
}
