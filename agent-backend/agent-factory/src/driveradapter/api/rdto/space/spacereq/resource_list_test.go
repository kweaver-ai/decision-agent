package spacereq

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestResourceListReq_GetErrMsgMap(t *testing.T) {
	t.Parallel()

	req := &ResourceListReq{}
	errMap := req.GetErrMsgMap()

	assert.NotNil(t, errMap)
}

func TestResourceListReq_StructFields(t *testing.T) {
	t.Parallel()

	req := &ResourceListReq{
		Name: "test-resource",
	}

	assert.NotNil(t, req)
	assert.Equal(t, "test-resource", req.Name)
}

func TestResourceListReq_Empty(t *testing.T) {
	t.Parallel()

	req := &ResourceListReq{}
	assert.NotNil(t, req)
	assert.Empty(t, req.Name)
}

func TestResourceListReq_WithNameFilter(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name string
		req  *ResourceListReq
	}{
		{
			name: "with name",
			req: &ResourceListReq{
				Name: "agent-1",
			},
		},
		{
			name: "empty name",
			req: &ResourceListReq{
				Name: "",
			},
		},
		{
			name: "with search term",
			req: &ResourceListReq{
				Name: "search-term",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			assert.NotNil(t, tt.req)
		})
	}
}
