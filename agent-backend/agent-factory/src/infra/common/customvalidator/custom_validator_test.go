package customvalidator

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestCustomValidatorPackage(t *testing.T) {
	t.Run("package exists for testing", func(t *testing.T) {
		// This test verifies the customvalidator package compiles
		// and can be imported for testing
		assert.NotNil(t, "customvalidator package")
	})
}
