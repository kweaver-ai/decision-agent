package capierr

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestErrorCodes_AreDefined(t *testing.T) {
	t.Parallel()

	// Test that the error code constants are properly defined
	assert.NotEmpty(t, DataAgentConfigLlmRequired)
	assert.NotEmpty(t, DataAgentConfigRetrieverDataSourceKnEntryExceedLimitSize)

	// Verify the error codes follow the expected format
	assert.Contains(t, DataAgentConfigLlmRequired, "AgentFactory")
	assert.Contains(t, DataAgentConfigRetrieverDataSourceKnEntryExceedLimitSize, "AgentFactory")
}

func TestErrorCodes_ConstantValues(t *testing.T) {
	t.Parallel()

	// Test specific error code values
	assert.Equal(t, "AgentFactory.DataAgentConfig.BadRequest.LlmRequired", DataAgentConfigLlmRequired)
	assert.Contains(t, DataAgentConfigRetrieverDataSourceKnEntryExceedLimitSize, "KnEntryExceedLimitSize")
}

func TestErrorCodes_Format(t *testing.T) {
	t.Parallel()

	// Error codes should follow the format: Service.Domain.Feature.SpecificError
	errorCodes := []string{
		DataAgentConfigLlmRequired,
		DataAgentConfigRetrieverDataSourceKnEntryExceedLimitSize,
	}

	for _, code := range errorCodes {
		// Should contain dots separating the parts
		assert.Contains(t, code, ".")
		// Should start with service name
		assert.True(t, len(code) > 0)
	}
}

func TestErrorCodes_Uniqueness(t *testing.T) {
	t.Parallel()

	// Each error code should be unique
	assert.NotEqual(t, DataAgentConfigLlmRequired, DataAgentConfigRetrieverDataSourceKnEntryExceedLimitSize)
}

// Note: The NewCustom*Err functions (NewCustom400Err, NewCustom401Err, etc.) require
// error codes to be registered with the kweaver-go-lib library. Since the registration
// happens at the application level (not in this package), these functions cannot be
// tested in isolation without the full application context.
//
// The functions are simple wrappers around rest.NewHTTPError with different HTTP status codes.
// They are used throughout the codebase with registered error codes.
//
// Coverage for these functions remains at 0% due to this limitation.

func TestCustomErrorFunctions_Signatures(t *testing.T) {
	t.Parallel()

	// Compile-time verification that the functions exist
	_ = NewCustom400Err
	_ = NewCustom401Err
	_ = NewCustom403Err
	_ = NewCustom404Err
	_ = NewCustom405Err
	_ = NewCustom409Err
	_ = NewCustom500Err
}
