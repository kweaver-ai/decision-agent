package observabilityhandler

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestNewObservabilityHTTPHandler_NotNil(t *testing.T) {
	h := NewObservabilityHTTPHandler()
	require.NotNil(t, h)
}
