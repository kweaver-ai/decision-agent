package agentrespvo

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestDocRetrievalField_New(t *testing.T) {
	field := &DocRetrievalField{
		Text: "test text",
	}

	assert.NotNil(t, field)
	assert.Equal(t, "test text", field.Text)
	assert.Nil(t, field.Cites)
}

func TestDocRetrievalField_WithCites(t *testing.T) {
	cites := []*CiteDoc{
		{
			DocID:   "doc-1",
			DocName: "Test Document",
		},
	}

	field := &DocRetrievalField{
		Text:  "test text",
		Cites: cites,
	}

	assert.Equal(t, "test text", field.Text)
	assert.Len(t, field.Cites, 1)
	assert.Equal(t, "doc-1", field.Cites[0].DocID)
}

func TestGraphRetrievalField_New(t *testing.T) {
	field := &GraphRetrievalField{
		KGID:   "kg-1",
		KGName: "Test KG",
		Text:   "test text",
	}

	assert.NotNil(t, field)
	assert.Equal(t, "kg-1", field.KGID)
	assert.Equal(t, "Test KG", field.KGName)
	assert.Equal(t, "test text", field.Text)
}

func TestCiteDoc_New(t *testing.T) {
	cite := &CiteDoc{
		Content:    "test content",
		ExtType:    ".txt",
		DocID:      "gns://123",
		DocName:    "test.txt",
		ObjectID:   "456",
		ParentPath: "/path/to/file",
		Size:       1024,
		Type:       "document",
		SpaceID:    "space-1",
		DocLibType: "knowledge_doc_lib",
	}

	assert.NotNil(t, cite)
	assert.Equal(t, "test content", cite.Content)
	assert.Equal(t, ".txt", cite.ExtType)
	assert.Equal(t, "gns://123", cite.DocID)
	assert.Equal(t, int64(1024), cite.Size)
}

func TestCiteDoc_WithSlices(t *testing.T) {
	slices := []*V1Slice{
		{
			ID:      "slice-1",
			No:      1,
			Content: "slice content",
			Pages:   []int{1, 2},
		},
	}

	cite := &CiteDoc{
		DocID:  "doc-1",
		Slices: slices,
	}

	assert.Len(t, cite.Slices, 1)
	assert.Equal(t, "slice-1", cite.Slices[0].ID)
	assert.Equal(t, 1, cite.Slices[0].No)
	assert.Equal(t, []int{1, 2}, cite.Slices[0].Pages)
}

func TestV1Slice_New(t *testing.T) {
	slice := &V1Slice{
		ID:      "slice-1",
		No:      1,
		Content: "slice content",
		Pages:   []int{1, 2, 3},
	}

	assert.NotNil(t, slice)
	assert.Equal(t, "slice-1", slice.ID)
	assert.Equal(t, 1, slice.No)
	assert.Equal(t, "slice content", slice.Content)
	assert.Equal(t, []int{1, 2, 3}, slice.Pages)
}

func TestV1Slice_EmptyPages(t *testing.T) {
	slice := &V1Slice{
		ID:    "slice-1",
		No:    1,
		Pages: []int{},
	}

	assert.NotNil(t, slice)
	assert.Empty(t, slice.Pages)
}

func TestGraphRetrievalField_WithSubgraph(t *testing.T) {
	subgraph := map[string]interface{}{
		"nodes": []string{"node1", "node2"},
	}

	field := &GraphRetrievalField{
		Subgraph: subgraph,
		Text:     "test text",
	}

	assert.NotNil(t, field.Subgraph)
	assert.Equal(t, "test text", field.Text)
}

func TestCiteDoc_AllFields(t *testing.T) {
	cite := &CiteDoc{
		Content:     "This is a test document content",
		ExtType:     ".pdf",
		DocID:       "gns://ABC123/DEF456",
		DocName:     "Test Document.pdf",
		ObjectID:    "DEF456",
		ParentPath:  "/folder/subfolder",
		Size:        2048000,
		Type:        "document",
		SpaceID:     "space-123",
		DocLibType:  "knowledge_doc_lib",
		Slices:      []*V1Slice{},
	}

	assert.Equal(t, "This is a test document content", cite.Content)
	assert.Equal(t, ".pdf", cite.ExtType)
	assert.Equal(t, "gns://ABC123/DEF456", cite.DocID)
	assert.Equal(t, "Test Document.pdf", cite.DocName)
	assert.Equal(t, int64(2048000), cite.Size)
	assert.Equal(t, "space-123", cite.SpaceID)
}
