package cconstant

import (
	"testing"
)

func TestRequestConstants(t *testing.T) {
	t.Run("NameMaxLength constant", func(t *testing.T) {
		if NameMaxLength != 50 {
			t.Errorf("Expected NameMaxLength to be 50, got %d", NameMaxLength)
		}
	})

	t.Run("ProfileMaxLength constant", func(t *testing.T) {
		if ProfileMaxLength != 100 {
			t.Errorf("Expected ProfileMaxLength to be 100, got %d", ProfileMaxLength)
		}
	})
}
