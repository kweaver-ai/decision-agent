package agentconfigvo

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewOutputVariablesS(t *testing.T) {
	vars := NewOutputVariablesS()
	assert.NotNil(t, vars)
	assert.IsType(t, &OutputVariablesS{}, vars)
}

func TestExtractOutputFromLine(t *testing.T) {
	tests := []struct {
		name string
		line string
		want string
	}{
		{
			name: "包含->和output_",
			line: " -> output_test",
			want: "output_test",
		},
		{
			name: "包含>>和output_",
			line: ">> output_value",
			want: "output_value",
		},
		{
			name: "不包含output_",
			line: " some text",
			want: "",
		},
		{
			name: "空行",
			line: "",
			want: "",
		},
		{
			name: "只有->没有output_",
			line: " -> something",
			want: "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := extractOutputFromLine(tt.line)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestExtractOutputsFromText(t *testing.T) {
	tests := []struct {
		name      string
		text      string
		wantCount int
	}{
		{
			name:      "单个output",
			text:      " -> output_test",
			wantCount: 1,
		},
		{
			name:      "多个output",
			text:      " -> output1\n -> output2\n>> output3",
			wantCount: 3,
		},
		{
			name:      "混合内容",
			text:      "some text\n -> output_test\nmore text",
			wantCount: 1,
		},
		{
			name:      "空文本",
			text:      "",
			wantCount: 0,
		},
		{
			name:      "没有output",
			text:      "just some text",
			wantCount: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			outputs, err := ExtractOutputsFromText(tt.text)
			assert.NoError(t, err)
			assert.Len(t, outputs, tt.wantCount)
		})
	}
}

func TestExtractOutputsFromText_Errors(t *testing.T) {
	tests := []struct {
		name string
		text string
	}{
		{
			name: "空白符",
			text: "   ",
		},
		{
			name: "多行空白符",
			text: "  \n  \n  ",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			outputs, err := ExtractOutputsFromText(tt.text)
			assert.NoError(t, err)
			assert.Len(t, outputs, 0)
		})
	}
}
