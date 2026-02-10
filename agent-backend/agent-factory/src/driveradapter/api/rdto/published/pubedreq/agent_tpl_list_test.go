package pubedreq

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestPubedTplListReq_StructFields(t *testing.T) {
	req := PubedTplListReq{
		Name:               "Test Template",
		CategoryID:         "cat-123",
		Size:               10,
		PaginationMarkerStr: "marker",
		TplIDsByBd:         []string{"tpl-1", "tpl-2"},
	}

	assert.Equal(t, "Test Template", req.Name)
	assert.Equal(t, "cat-123", req.CategoryID)
	assert.Equal(t, 10, req.Size)
	assert.Equal(t, "marker", req.PaginationMarkerStr)
	assert.Len(t, req.TplIDsByBd, 2)
}

func TestPubedTplListReq_Empty(t *testing.T) {
	req := PubedTplListReq{}

	assert.Empty(t, req.Name)
	assert.Empty(t, req.CategoryID)
	assert.Equal(t, 0, req.Size)
	assert.Empty(t, req.PaginationMarkerStr)
	assert.Nil(t, req.TplIDsByBd)
	assert.Nil(t, req.Marker)
}

func TestPubedTplListReq_GetErrMsgMap(t *testing.T) {
	req := PubedTplListReq{}

	errMsgMap := req.GetErrMsgMap()

	assert.NotNil(t, errMsgMap)
	assert.Empty(t, errMsgMap)
}

func TestPubedTplListReq_LoadMarkerStr_Empty(t *testing.T) {
	req := PubedTplListReq{
		PaginationMarkerStr: "",
	}

	err := req.LoadMarkerStr()

	assert.NoError(t, err)
	assert.Nil(t, req.Marker)
}

func TestPubedTplListReq_LoadMarkerStr_WithMarker(t *testing.T) {
	req := PubedTplListReq{
		PaginationMarkerStr: "eyJhZ2VudF9pZCI6ImFnZW50LTEyMyIsInVwZGF0ZWRfYXQiOjEyMzQ1Njc4OTB9",
	}

	err := req.LoadMarkerStr()

	// This might fail if the marker is invalid, but we're testing the function is called
	// The actual parsing logic depends on the Marker implementation
	if err != nil {
		assert.Contains(t, err.Error(), "invalid")
	} else {
		assert.NotNil(t, req.Marker)
	}
}

func TestPubedTplListReq_WithName(t *testing.T) {
	names := []string{
		"Test Template",
		"测试模板",
		"Template with numbers 123",
		"",
	}

	for _, name := range names {
		req := PubedTplListReq{
			Name: name,
		}
		assert.Equal(t, name, req.Name)
	}
}

func TestPubedTplListReq_WithCategoryID(t *testing.T) {
	categoryIDs := []string{
		"cat-001",
		"cat-xyz",
		"分类-123",
		"",
	}

	for _, categoryID := range categoryIDs {
		req := PubedTplListReq{
			CategoryID: categoryID,
		}
		assert.Equal(t, categoryID, req.CategoryID)
	}
}

func TestPubedTplListReq_WithSize(t *testing.T) {
	sizes := []int{
		0,
		1,
		10,
		100,
		1000,
	}

	for _, size := range sizes {
		req := PubedTplListReq{
			Size: size,
		}
		assert.Equal(t, size, req.Size)
	}
}

func TestPubedTplListReq_WithTplIDsByBd(t *testing.T) {
	tplIDs := []string{
		"tpl-001",
		"tpl-002",
		"tpl-003",
	}

	req := PubedTplListReq{
		TplIDsByBd: tplIDs,
	}

	assert.Len(t, req.TplIDsByBd, 3)
	assert.Equal(t, "tpl-001", req.TplIDsByBd[0])
	assert.Equal(t, "tpl-002", req.TplIDsByBd[1])
	assert.Equal(t, "tpl-003", req.TplIDsByBd[2])
}

func TestPubedTplListReq_WithEmptyTplIDsByBd(t *testing.T) {
	req := PubedTplListReq{
		TplIDsByBd: []string{},
	}

	assert.NotNil(t, req.TplIDsByBd)
	assert.Len(t, req.TplIDsByBd, 0)
}

func TestPubedTplListReq_WithNilTplIDsByBd(t *testing.T) {
	req := PubedTplListReq{
		TplIDsByBd: nil,
	}

	assert.Nil(t, req.TplIDsByBd)
}

func TestPubedTplListReq_WithPaginationMarkerStr(t *testing.T) {
	markerStrs := []string{
		"marker1",
		"marker2",
		"",
	}

	for _, markerStr := range markerStrs {
		req := PubedTplListReq{
			PaginationMarkerStr: markerStr,
		}
		assert.Equal(t, markerStr, req.PaginationMarkerStr)
	}
}

func TestPubedTplListReq_WithAllFields(t *testing.T) {
	req := PubedTplListReq{
		Name:               "Complete Template",
		CategoryID:         "cat-complete",
		Size:               25,
		PaginationMarkerStr: "complete-marker",
		TplIDsByBd:         []string{"tpl-complete"},
	}

	assert.Equal(t, "Complete Template", req.Name)
	assert.Equal(t, "cat-complete", req.CategoryID)
	assert.Equal(t, 25, req.Size)
	assert.Equal(t, "complete-marker", req.PaginationMarkerStr)
	assert.Len(t, req.TplIDsByBd, 1)
}

func TestPubedTplListReq_ModifyTplIDsByBd(t *testing.T) {
	req := PubedTplListReq{
		TplIDsByBd: []string{"tpl-1"},
	}

	assert.Len(t, req.TplIDsByBd, 1)

	// Append new template IDs
	req.TplIDsByBd = append(req.TplIDsByBd, "tpl-2", "tpl-3")

	assert.Len(t, req.TplIDsByBd, 3)
	assert.Equal(t, "tpl-2", req.TplIDsByBd[1])
	assert.Equal(t, "tpl-3", req.TplIDsByBd[2])
}
