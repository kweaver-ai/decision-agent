package csconstant

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestMaxResourceNumInOneSpace(t *testing.T) {
	assert.Equal(t, 500, MaxResourceNumInOneSpace)
}

func TestMaxResourceNumInOneSpace_IsPositive(t *testing.T) {
	assert.Greater(t, MaxResourceNumInOneSpace, 0)
}
