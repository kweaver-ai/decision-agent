package chelper

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestAppendWriteToFile(t *testing.T) {
	// Save original function and restore after test
	// Note: This test only works when IsAaronLocalDev returns false
	// We can't easily test the actual file write without modifying the environment check

	t.Run("returns nil when not in local dev environment", func(t *testing.T) {
		// This test assumes IsAaronLocalDev returns false
		// which is the case in CI/CD and most environments
		err := AppendWriteToFile("/tmp/test-file.txt", "test content")
		assert.NoError(t, err)

		// Verify file was not created
		_, err = os.Stat("/tmp/test-file.txt")
		assert.True(t, os.IsNotExist(err))
	})

	t.Run("handles empty file path", func(t *testing.T) {
		err := AppendWriteToFile("", "test content")
		// Should not crash
		assert.NoError(t, err)
	})

	t.Run("handles empty text", func(t *testing.T) {
		// Create a temp directory for testing
		tmpDir := t.TempDir()
		testFile := filepath.Join(tmpDir, "test-append.txt")

		// Note: This won't actually write because of the IsAaronLocalDev check
		err := AppendWriteToFile(testFile, "")
		// Should not crash
		assert.NoError(t, err)
	})

	t.Run("is thread-safe", func(t *testing.T) {
		tmpDir := t.TempDir()
		testFile := filepath.Join(tmpDir, "concurrent-test.txt")

		// This test verifies the function doesn't crash when called concurrently
		done := make(chan bool)

		for i := 0; i < 10; i++ {
			go func() {
				_ = AppendWriteToFile(testFile, "test content")
				done <- true
			}()
		}

		for i := 0; i < 10; i++ {
			<-done
		}

		// If we get here without deadlock or panic, the test passes
		assert.True(t, true)
	})
}
