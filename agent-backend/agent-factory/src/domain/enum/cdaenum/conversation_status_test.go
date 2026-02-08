package cdaenum

import (
	"testing"
)

func TestConversationStatus_Constants(t *testing.T) {
	t.Run("ConvStatusProcessing constant", func(t *testing.T) {
		if ConvStatusProcessing != "processing" {
			t.Errorf("Expected ConvStatusProcessing to be 'processing', got '%s'", ConvStatusProcessing)
		}
	})

	t.Run("ConvStatusCompleted constant", func(t *testing.T) {
		if ConvStatusCompleted != "completed" {
			t.Errorf("Expected ConvStatusCompleted to be 'completed', got '%s'", ConvStatusCompleted)
		}
	})

	t.Run("ConvStatusCancelled constant", func(t *testing.T) {
		if ConvStatusCancelled != "cancelled" {
			t.Errorf("Expected ConvStatusCancelled to be 'cancelled', got '%s'", ConvStatusCancelled)
		}
	})

	t.Run("ConvStatusFailed constant", func(t *testing.T) {
		if ConvStatusFailed != "failed" {
			t.Errorf("Expected ConvStatusFailed to be 'failed', got '%s'", ConvStatusFailed)
		}
	})
}
