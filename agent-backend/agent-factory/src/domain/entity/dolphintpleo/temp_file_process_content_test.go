package dolphintpleo

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/daconfvalobj"
)

func TestNewTempFileProcessContent(t *testing.T) {
	content := NewTempFileProcessContent()
	if content == nil {
		t.Error("NewTempFileProcessContent() should return non-nil")
	}
	if content.Content != "" {
		t.Errorf("Content should be empty, got %q", content.Content)
	}
}

func TestTempFileProcessContent_LoadFromConfig(t *testing.T) {
	tests := []struct {
		name        string
		config      *daconfvalobj.Config
		wantIsEnable bool
	}{
		{
			name: "temp zone enabled",
			config: &daconfvalobj.Config{
				Input: &daconfvalobj.Input{
					IsTempZoneEnabled: cdaenum.TempZoneEnabled,
				},
			},
			wantIsEnable: true,
		},
		{
			name: "temp zone disabled",
			config: &daconfvalobj.Config{
				Input: &daconfvalobj.Input{
					IsTempZoneEnabled: cdaenum.TempZoneDisabled,
				},
			},
			wantIsEnable: false,
		},
		{
			name:        "nil config",
			config:      nil,
			wantIsEnable: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			content := NewTempFileProcessContent()
			content.LoadFromConfig(tt.config)
			if content.IsEnable != tt.wantIsEnable {
				t.Errorf("IsEnable = %v, want %v", content.IsEnable, tt.wantIsEnable)
			}
		})
	}
}

func TestTempFileProcessContent_ToString(t *testing.T) {
	content := NewTempFileProcessContent()
	content.Content = "test content"

	result := content.ToString()
	if result != "\n test content \n " {
		t.Errorf("ToString() = %q, want %q", result, "\n test content \n ")
	}
}

func TestTempFileProcessContent_ToDolphinTplEo(t *testing.T) {
	content := NewTempFileProcessContent()
	content.Content = "test"

	eo := content.ToDolphinTplEo()
	if eo.Key != cdaenum.DolphinTplKeyTempFileProcess {
		t.Errorf("Key = %v, want %v", eo.Key, cdaenum.DolphinTplKeyTempFileProcess)
	}
	if eo.Value != "\n test \n " {
		t.Errorf("Value = %q, want %q", eo.Value, "\n test \n ")
	}
}
