package capierr

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestErrorCodes_AreDefined(t *testing.T) {
	// Test that the error code constants are properly defined
	assert.NotEmpty(t, DataAgentConfigLlmRequired)
	assert.NotEmpty(t, DataAgentConfigRetrieverDataSourceKnEntryExceedLimitSize)

	// Verify the error codes follow the expected format
	assert.Contains(t, DataAgentConfigLlmRequired, "AgentFactory")
	assert.Contains(t, DataAgentConfigRetrieverDataSourceKnEntryExceedLimitSize, "AgentFactory")
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




