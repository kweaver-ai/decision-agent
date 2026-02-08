package capierr

import (
	"testing"
)

func TestDataAgentConfigErrorCodes(t *testing.T) {
	t.Run("DataAgentConfigLlmRequired constant", func(t *testing.T) {
		expected := "AgentFactory.DataAgentConfig.BadRequest.LlmRequired"
		if DataAgentConfigLlmRequired != expected {
			t.Errorf("Expected DataAgentConfigLlmRequired to be '%s', got '%s'", expected, DataAgentConfigLlmRequired)
		}
	})

	t.Run("DataAgentConfigRetrieverDataSourceKnEntryExceedLimitSize constant", func(t *testing.T) {
		expected := "AgentFactory.DataAgentConfig.BadRequest.RetrieverDataSourceKnEntryExceedLimitSize"
		if DataAgentConfigRetrieverDataSourceKnEntryExceedLimitSize != expected {
			t.Errorf("Expected DataAgentConfigRetrieverDataSourceKnEntryExceedLimitSize to be '%s', got '%s'", expected, DataAgentConfigRetrieverDataSourceKnEntryExceedLimitSize)
		}
	})

	t.Run("error codes are unique", func(t *testing.T) {
		if DataAgentConfigLlmRequired == DataAgentConfigRetrieverDataSourceKnEntryExceedLimitSize {
			t.Error("Error codes should be unique")
		}
	})

	t.Run("error codes are not empty", func(t *testing.T) {
		if DataAgentConfigLlmRequired == "" {
			t.Error("DataAgentConfigLlmRequired should not be empty")
		}
		if DataAgentConfigRetrieverDataSourceKnEntryExceedLimitSize == "" {
			t.Error("DataAgentConfigRetrieverDataSourceKnEntryExceedLimitSize should not be empty")
		}
	})
}
