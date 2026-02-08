package cconstant

import (
	"testing"
)

func TestUniqueIDFlag(t *testing.T) {
	t.Run("UniqueIDFlag type exists", func(t *testing.T) {
		// Test that we can create variables of UniqueIDFlag type
		var flag UniqueIDFlag
		_ = flag
	})

	t.Run("UniqueIDFlagDB constant", func(t *testing.T) {
		expected := UniqueIDFlag(1)
		if UniqueIDFlagDB != expected {
			t.Errorf("Expected UniqueIDFlagDB to be %d, got %d", expected, UniqueIDFlagDB)
		}
	})

	t.Run("UniqueIDFlagRedisDlm constant", func(t *testing.T) {
		expected := UniqueIDFlag(2)
		if UniqueIDFlagRedisDlm != expected {
			t.Errorf("Expected UniqueIDFlagRedisDlm to be %d, got %d", expected, UniqueIDFlagRedisDlm)
		}
	})

	t.Run("flags are unique", func(t *testing.T) {
		if UniqueIDFlagDB == UniqueIDFlagRedisDlm {
			t.Error("UniqueIDFlagDB and UniqueIDFlagRedisDlm should be different")
		}
	})

	t.Run("assign flag to variable", func(t *testing.T) {
		var flag UniqueIDFlag = UniqueIDFlagDB
		if flag != UniqueIDFlagDB {
			t.Errorf("Expected flag to be UniqueIDFlagDB, got %d", flag)
		}
	})
}
