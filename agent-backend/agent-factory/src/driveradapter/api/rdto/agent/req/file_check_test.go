package agentreq

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestFileCheckReq_Type(t *testing.T) {
	// FileCheckReq is a slice type
	var req FileCheckReq

	assert.Nil(t, req)
	assert.IsType(t, FileCheckReq{}, req)
}

func TestFileCheckReq_Empty(t *testing.T) {
	req := FileCheckReq{}

	assert.Empty(t, req)
	assert.Len(t, req, 0)
}

func TestFileCheckReq_WithItems(t *testing.T) {
	req := FileCheckReq{
		{
			ID: "check-1",
		},
		{
			ID: "check-2",
		},
	}

	assert.Len(t, req, 2)
	assert.Equal(t, "check-1", req[0].ID)
	assert.Equal(t, "check-2", req[1].ID)
}

func TestFileCheck_StructFields(t *testing.T) {
	check := FileCheck{
		ID: "check-123",
	}

	assert.Equal(t, "check-123", check.ID)
}

func TestFileCheck_Empty(t *testing.T) {
	check := FileCheck{}

	assert.Empty(t, check.ID)
}

func TestFileCheckReq_WithMultipleIDs(t *testing.T) {
	ids := []string{
		"check-001",
		"check-002",
		"check-003",
		"check-004",
		"check-005",
	}

	req := FileCheckReq{}
	for _, id := range ids {
		req = append(req, FileCheck{
			ID: id,
		})
	}

	assert.Len(t, req, 5)
	assert.Equal(t, "check-001", req[0].ID)
	assert.Equal(t, "check-005", req[4].ID)
}

func TestFileCheckReq_SliceOperations(t *testing.T) {
	req := FileCheckReq{
		{ID: "check-1"},
		{ID: "check-2"},
		{ID: "check-3"},
	}

	// Test length
	assert.Len(t, req, 3)

	// Test slicing
	subReq := req[1:3]
	assert.Len(t, subReq, 2)
	assert.Equal(t, "check-2", subReq[0].ID)
	assert.Equal(t, "check-3", subReq[1].ID)

	// Test iteration
	count := 0
	for _, check := range req {
		assert.NotEmpty(t, check.ID)
		count++
	}
	assert.Equal(t, 3, count)
}

func TestFileCheckReq_Capacity(t *testing.T) {
	req := make(FileCheckReq, 0, 100)

	assert.Len(t, req, 0)
	assert.NotNil(t, req)

	// Test that we can append up to capacity
	for i := 0; i < 100; i++ {
		req = append(req, FileCheck{
			ID: "check-" + string(rune(i)),
		})
	}

	assert.Len(t, req, 100)
}

func TestFileCheck_WithDifferentIDs(t *testing.T) {
	ids := []string{
		"check-001",
		"check-xyz",
		"检查-123",
		"",
	}

	for _, id := range ids {
		check := FileCheck{
			ID: id,
		}
		assert.Equal(t, id, check.ID)
	}
}

func TestFileCheckReq_WithDuplicateIDs(t *testing.T) {
	req := FileCheckReq{
		{ID: "check-dup"},
		{ID: "check-dup"},
		{ID: "check-unique"},
	}

	assert.Len(t, req, 3)
	assert.Equal(t, "check-dup", req[0].ID)
	assert.Equal(t, "check-dup", req[1].ID)
	assert.Equal(t, "check-unique", req[2].ID)
}

func TestFileCheckReq_Append(t *testing.T) {
	req := FileCheckReq{}

	req = append(req, FileCheck{ID: "check-1"})
	req = append(req, FileCheck{ID: "check-2"})
	req = append(req, FileCheck{ID: "check-3"})

	assert.Len(t, req, 3)
	assert.Equal(t, "check-1", req[0].ID)
	assert.Equal(t, "check-2", req[1].ID)
	assert.Equal(t, "check-3", req[2].ID)
}
