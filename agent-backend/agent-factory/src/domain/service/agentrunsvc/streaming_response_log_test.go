package agentsvc

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewStreamingResponseLogger_NonDebugMode(t *testing.T) {
	os.Unsetenv("APP_DEBUG")

	logger, err := NewStreamingResponseLogger("conv-123", ExecutorResponse)

	assert.NoError(t, err)
	assert.Nil(t, logger)
}

func TestStreamingResponseLogger_LogChunk_NilLogger(t *testing.T) {
	var l *StreamingResponseLogger

	assert.NotPanics(t, func() {
		l.LogChunk([]byte("test chunk"))
	})
}

func TestStreamingResponseLogger_Complete_NilLogger(t *testing.T) {
	var l *StreamingResponseLogger

	assert.NotPanics(t, func() {
		l.Complete()
	})
}

func TestStreamingResponseLogger_LogChunk_NilFile(t *testing.T) {
	l := &StreamingResponseLogger{
		file: nil,
	}

	assert.NotPanics(t, func() {
		l.LogChunk([]byte("test chunk"))
	})
}

func TestStreamingResponseLogger_Complete_NilFile(t *testing.T) {
	l := &StreamingResponseLogger{
		file: nil,
	}

	assert.NotPanics(t, func() {
		l.Complete()
	})
}

func TestStreamingResponseLogger_LogAndComplete_WithRealFile(t *testing.T) {
	tmpDir := t.TempDir()
	f, err := os.CreateTemp(tmpDir, "test-*.log")
	if err != nil {
		t.Fatal(err)
	}

	l := &StreamingResponseLogger{
		file:           f,
		conversationID: "conv-test",
		logType:        ProcessedResponse,
	}

	l.LogChunk([]byte("hello"))
	l.LogChunk([]byte("world"))
	assert.Equal(t, 2, l.chunksCount)
	assert.Equal(t, 10, l.totalBytes)

	l.Complete()
}
