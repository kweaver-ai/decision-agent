package agentsvc

import (
	"testing"
)

func TestStreamingResponseLogger_LogChunk_NilLogger(t *testing.T) {
	// Test that LogChunk doesn't panic on nil receiver
	var logger *StreamingResponseLogger
	logger.LogChunk([]byte("test")) // Should not panic
}

func TestStreamingResponseLogger_Complete_NilLogger(t *testing.T) {
	// Test that Complete doesn't panic on nil receiver
	var logger *StreamingResponseLogger
	logger.Complete() // Should not panic
}

func TestStreamingResponseLogger_LogChunk_NilFile(t *testing.T) {
	logger := &StreamingResponseLogger{file: nil}
	logger.LogChunk([]byte("test")) // Should not panic
}

func TestStreamingResponseLogger_Complete_NilFile(t *testing.T) {
	logger := &StreamingResponseLogger{file: nil}
	logger.Complete() // Should not panic
}

func TestResponseLoggerType_String(t *testing.T) {
	if ExecutorResponse != "executor_res" {
		t.Errorf("Expected ExecutorResponse to be 'executor_res', got '%s'", ExecutorResponse)
	}
	if ProcessedResponse != "processed_res" {
		t.Errorf("Expected ProcessedResponse to be 'processed_res', got '%s'", ProcessedResponse)
	}
}

func TestStreamingResponseLogger_LogChunk_EmptyChunk(t *testing.T) {
	logger := &StreamingResponseLogger{file: nil}
	logger.LogChunk([]byte{}) // Should not panic with empty chunk
}

func TestStreamingResponseLogger_Constants(t *testing.T) {
	tests := []struct {
		name  string
		value ResponseLoggerType
		want  string
	}{
		{"ExecutorResponse", ExecutorResponse, "executor_res"},
		{"ProcessedResponse", ProcessedResponse, "processed_res"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if string(tt.value) != tt.want {
				t.Errorf("Expected %s to be %s, got %s", tt.name, tt.want, tt.value)
			}
		})
	}
}
