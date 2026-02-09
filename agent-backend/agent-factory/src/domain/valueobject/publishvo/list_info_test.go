package publishvo

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewListPublishInfo(t *testing.T) {
	info := NewListPublishInfo()

	assert.NotNil(t, info)
	assert.NotNil(t, info.PublishedToBeStruct)
}

func TestNewListPublishInfo_CreatesNewInstance(t *testing.T) {
	info1 := NewListPublishInfo()
	info2 := NewListPublishInfo()

	assert.NotNil(t, info1)
	assert.NotNil(t, info2)
	// Both instances are valid
	assert.NotNil(t, info1.PublishedToBeStruct)
	assert.NotNil(t, info2.PublishedToBeStruct)
}

func TestListPublishInfo_Empty(t *testing.T) {
	info := &ListPublishInfo{}

	assert.NotNil(t, info)
	assert.NotNil(t, info.PublishedToBeStruct)
}
