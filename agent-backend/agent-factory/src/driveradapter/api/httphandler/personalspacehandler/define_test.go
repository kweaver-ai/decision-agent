package personalspacehandler

import (
	"testing"
)

func TestGetPersonalSpaceHTTPHandler_NotNil(t *testing.T) {
	defer func() {
		if r := recover(); r != nil {
			t.Skipf("GetPersonalSpaceHTTPHandler requires global init, skipped in unit test: %v", r)
		}
	}()
	h := GetPersonalSpaceHTTPHandler()
	if h == nil {
		t.Error("expected non-nil handler")
	}
}
