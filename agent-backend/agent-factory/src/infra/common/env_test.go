package common

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestIsDisablePmsCheck(t *testing.T) {
	result := IsDisablePmsCheck()
	assert.NotNil(t, result, "IsDisablePmsCheck() should return boolean")
	assert.IsType(t, false, result, "IsDisablePmsCheck() should return bool type")
}
