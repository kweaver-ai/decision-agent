package spacereq

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestListReq_StructFields(t *testing.T) {
	req := ListReq{
		Name: "Test Space",
	}
	req.Size = 10
	req.Page = 1

	assert.Equal(t, "Test Space", req.Name)
	assert.Equal(t, 10, req.Size)
	assert.Equal(t, 1, req.Page)
}

func TestListReq_Empty(t *testing.T) {
	req := ListReq{}

	assert.Empty(t, req.Name)
	assert.Equal(t, 0, req.Size)
	assert.Equal(t, 0, req.Page)
}

func TestListReq_GetErrMsgMap(t *testing.T) {
	req := ListReq{}

	errMsgMap := req.GetErrMsgMap()

	assert.NotNil(t, errMsgMap)
}

func TestListReq_WithPagination(t *testing.T) {
	req := ListReq{}
	req.Size = 20
	req.Page = 2

	offset := req.GetOffset()
	assert.Equal(t, 20, offset)
}

func TestListReq_WithDefaultPagination(t *testing.T) {
	req := ListReq{}
	// PageSize has default values when Size is 0
	req.Size = 0
	req.Page = 0

	offset := req.GetOffset()
	assert.Equal(t, 0, offset)
}

func TestListReq_WithName(t *testing.T) {
	names := []string{
		"Test Space",
		"中文空间",
		"Space with numbers 123",
		"",
	}

	for _, name := range names {
		req := ListReq{
			Name: name,
		}
		assert.Equal(t, name, req.Name)
	}
}

func TestListReq_PaginationEdgeCases(t *testing.T) {
	tests := []struct {
		name     string
		page     int
		size     int
		expected int
	}{
		{
			name:     "first page",
			page:     1,
			size:     10,
			expected: 0,
		},
		{
			name:     "second page",
			page:     2,
			size:     10,
			expected: 10,
		},
		{
			name:     "large page number",
			page:     100,
			size:     20,
			expected: 1980,
		},
		{
			name:     "zero page",
			page:     0,
			size:     10,
			expected: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := ListReq{}
			req.Page = tt.page
			req.Size = tt.size

			offset := req.GetOffset()
			assert.Equal(t, tt.expected, offset)
		})
	}
}

func TestListReq_EmbeddedPageSize(t *testing.T) {
	req := ListReq{}

	// Verify that PageSize is embedded
	assert.IsType(t, req.Size, 0)
	assert.IsType(t, req.Page, 0)

	// Set and verify pagination values
	req.Size = 15
	req.Page = 3

	assert.Equal(t, 15, req.Size)
	assert.Equal(t, 3, req.Page)
	assert.Equal(t, 30, req.GetOffset())
}

func TestListReq_WithNameFilter(t *testing.T) {
	req := ListReq{
		Name: "My Space",
	}
	req.Size = 5
	req.Page = 1

	assert.Equal(t, "My Space", req.Name)
	assert.Equal(t, 5, req.Size)
	assert.Equal(t, 1, req.Page)
	assert.Equal(t, 0, req.GetOffset())
}

func TestListReq_WithEmptyName(t *testing.T) {
	req := ListReq{
		Name: "",
	}
	req.Size = 10
	req.Page = 1

	assert.Empty(t, req.Name)
	assert.Equal(t, 10, req.Size)
	assert.Equal(t, 1, req.Page)
}
