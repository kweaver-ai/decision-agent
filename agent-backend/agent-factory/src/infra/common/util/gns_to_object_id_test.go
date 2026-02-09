package util

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestGNS2ObjectID_ValidGNS(t *testing.T) {
	gns := "gns://doc/123/456"
	result := GNS2ObjectID(gns)

	assert.Equal(t, "456", result)
}

func TestGNS2ObjectID_SimpleGNS(t *testing.T) {
	gns := "gns://123"
	result := GNS2ObjectID(gns)

	assert.Equal(t, "123", result)
}

func TestGNS2ObjectID_SingleSlash(t *testing.T) {
	gns := "123/456"
	result := GNS2ObjectID(gns)

	assert.Equal(t, "456", result)
}

func TestGNS2ObjectID_SingleID(t *testing.T) {
	gns := "789"
	result := GNS2ObjectID(gns)

	assert.Equal(t, "789", result)
}

func TestGNS2ObjectID_MultipleSlashes(t *testing.T) {
	gns := "gns://doc/123/456/789/101112"
	result := GNS2ObjectID(gns)

	assert.Equal(t, "101112", result)
}

func TestGNS2ObjectID_EmptyString(t *testing.T) {
	gns := ""
	result := GNS2ObjectID(gns)

	// Split of empty string returns a slice with one empty string
	assert.Equal(t, "", result)
}

func TestGNS2ObjectID_TrailingSlash(t *testing.T) {
	gns := "gns://123/456/"
	result := GNS2ObjectID(gns)

	// Trailing slash results in empty string after the last slash
	assert.Equal(t, "", result)
}
