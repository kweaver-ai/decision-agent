package personalspacehandler

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestGetPersonalSpaceHTTPHandler_NotNil(t *testing.T) {
	h := GetPersonalSpaceHTTPHandler()
	require.NotNil(t, h)
}
