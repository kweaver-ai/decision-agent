package cconstant

import (
	"testing"
)

func TestPmsConstants(t *testing.T) {
	t.Run("PmsAllFlag constant", func(t *testing.T) {
		if PmsAllFlag != "*" {
			t.Errorf("Expected PmsAllFlag to be '*', got '%s'", PmsAllFlag)
		}
	})
}

func TestIsContainsPmsAllFlag(t *testing.T) {
	t.Run("contains PMS all flag", func(t *testing.T) {
		s := []string{"read", "write", "*"}
		result := IsContainsPmsAllFlag(s)

		if !result {
			t.Error("Expected result to be true when slice contains '*'")
		}
	})

	t.Run("does not contain PMS all flag", func(t *testing.T) {
		s := []string{"read", "write"}
		result := IsContainsPmsAllFlag(s)

		if result {
			t.Error("Expected result to be false when slice does not contain '*'")
		}
	})

	t.Run("empty slice", func(t *testing.T) {
		s := []string{}
		result := IsContainsPmsAllFlag(s)

		if result {
			t.Error("Expected result to be false for empty slice")
		}
	})

	t.Run("only PMS all flag", func(t *testing.T) {
		s := []string{"*"}
		result := IsContainsPmsAllFlag(s)

		if !result {
			t.Error("Expected result to be true when slice only contains '*'")
		}
	})
}
