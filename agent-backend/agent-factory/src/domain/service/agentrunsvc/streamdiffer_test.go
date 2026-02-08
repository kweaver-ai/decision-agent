package agentsvc

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestFormatSSEMessage(t *testing.T) {
	tests := []struct {
		name string
		data string
		want []byte
	}{
		{
			name: "formats data as SSE message",
			data: "test data",
			want: []byte("data: test data\n\n"),
		},
		{
			name: "handles empty data",
			data: "",
			want: []byte("data: \n\n"),
		},
		{
			name: "handles JSON data",
			data: `{"key":"value"}`,
			want: []byte("data: {\"key\":\"value\"}\n\n"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := formatSSEMessage(tt.data)
			assert.Equal(t, tt.want, result)
		})
	}
}

func TestFormatChange(t *testing.T) {
	tests := []struct {
		name string
		ch   Change
		want string
	}{
		{
			name: "formats change with string content",
			ch: Change{
				SeqID:   1,
				Key:     []interface{}{"path", "to", "field"},
				Content: "value",
				Action:  "upsert",
			},
			want: `{"seq_id": 1, "key": ["path","to","field"], "content": "value", "action": "upsert"}`,
		},
		{
			name: "formats change with numeric content",
			ch: Change{
				SeqID:   2,
				Key:     []interface{}{"count"},
				Content: 42,
				Action:  "append",
			},
			want: `{"seq_id": 2, "key": ["count"], "content": 42, "action": "append"}`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := formatChange(tt.ch)
			assert.Equal(t, tt.want, result)
		})
	}
}

func TestStreamDiff(t *testing.T) {
	ctx := context.Background()
	lastSeq := 0
	out := make(chan []byte, 100)

	t.Run("same JSON produces no changes", func(t *testing.T) {
		oldJSON := []byte(`{"name":"test","value":123}`)
		newJSON := []byte(`{"name":"test","value":123}`)

		err := StreamDiff(ctx, &lastSeq, oldJSON, newJSON, out)
		assert.NoError(t, err)
		assert.Empty(t, out)
	})

	t.Run("different objects produce changes", func(t *testing.T) {
		lastSeq = 0
		oldJSON := []byte(`{"name":"test","value":123}`)
		newJSON := []byte(`{"name":"test","value":456}`)

		err := StreamDiff(ctx, &lastSeq, oldJSON, newJSON, out)
		assert.NoError(t, err)
		assert.NotEmpty(t, out)
	})

	t.Run("string append produces append action", func(t *testing.T) {
		lastSeq = 0
		out = make(chan []byte, 100)
		oldJSON := []byte(`{"text":"hello"}`)
		newJSON := []byte(`{"text":"hello world"}`)

		err := StreamDiff(ctx, &lastSeq, oldJSON, newJSON, out)
		assert.NoError(t, err)
		assert.NotEmpty(t, out)
	})
}
