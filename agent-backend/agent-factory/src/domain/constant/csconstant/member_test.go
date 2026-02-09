package csconstant

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestMaxMemberNumInOneSpace(t *testing.T) {
	assert.Equal(t, 500, MaxMemberNumInOneSpace)
}

func TestMaxMemberNumInOneSpace_IsPositive(t *testing.T) {
	assert.Greater(t, MaxMemberNumInOneSpace, 0)
}
