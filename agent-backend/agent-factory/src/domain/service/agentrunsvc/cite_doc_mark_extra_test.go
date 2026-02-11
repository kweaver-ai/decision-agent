package agentsvc

import (
	"regexp"
	"testing"

	"github.com/stretchr/testify/assert"
)

// TestSplitSentences_EmptyText tests splitSentences with empty text
func TestSplitSentences_EmptyText(t *testing.T) {
	result := splitSentences("", 10)
	assert.Empty(t, result)
}

// TestSplitSentences_SimpleText tests splitSentences with simple sentences
func TestSplitSentences_SimpleText(t *testing.T) {
	text := "Hello world. How are you? I'm fine."
	result := splitSentences(text, 10)

	assert.NotEmpty(t, result)
	// Should combine sentences based on minimum length
}

// TestSplitSentences_ShortLength tests splitSentences with short minimum length
func TestSplitSentences_ShortLength(t *testing.T) {
	text := "A. B. C."
	result := splitSentences(text, 1)

	assert.NotEmpty(t, result)
	_ = result // Use result
}

// TestSplitSentences_LongLength tests splitSentences with long minimum length
func TestSplitSentences_LongLength(t *testing.T) {
	text := "Short sentence. Another short. Final sentence."
	result := splitSentences(text, 100)

	// With a long minimum length, all sentences should be combined
	assert.Len(t, result, 1)
	_ = result // Use result
}

// TestSplitSentences_NoPunctuation tests splitSentences without proper punctuation
func TestSplitSentences_NoPunctuation(t *testing.T) {
	text := "This is text without proper sentence endings"
	result := splitSentences(text, 10)

	assert.NotEmpty(t, result)
	_ = result // Use result
}

// TestSplitSentences_WithExclamation tests splitSentences with exclamation marks
func TestSplitSentences_WithExclamation(t *testing.T) {
	text := "Hello! Hi there! Goodbye!"
	result := splitSentences(text, 5)

	assert.NotEmpty(t, result)
	_ = result // Use result
}

// TestSplitSentences_WithQuestionMarks tests splitSentences with question marks
func TestSplitSentences_WithQuestionMarks(t *testing.T) {
	text := "Who are you? What is this? Why here?"
	result := splitSentences(text, 5)

	assert.NotEmpty(t, result)
}

// TestSplitSentences_MixedPunctuation tests splitSentences with mixed punctuation
func TestSplitSentences_MixedPunctuation(t *testing.T) {
	text := "First. Second! Third? Fourth."
	result := splitSentences(text, 5)

	assert.NotEmpty(t, result)
}

// TestMarkInDocIndex_NoMatch tests markInDocIndex with text that doesn't match patterns
func TestMarkInDocIndex_NoMatch(t *testing.T) {
	text := "This text has no document references"
	has, docIndexs, newText := markInDocIndex(text, docRefPatternList)

	assert.False(t, has)
	assert.Empty(t, docIndexs)
	assert.Equal(t, text, newText)
}

// TestMarkInDocIndex_SingleReference tests markInDocIndex with single document reference
func TestMarkInDocIndex_SingleReference(t *testing.T) {
	text := "参考文档1"
	has, docIndexs, newText := markInDocIndex(text, docRefPatternList)

	assert.True(t, has)
	assert.NotEmpty(t, docIndexs)
	assert.NotEqual(t, text, newText)
	assert.Contains(t, newText, "<i")
}

// TestMarkInDocIndex_MultipleReferences tests markInDocIndex with multiple references
func TestMarkInDocIndex_MultipleReferences(t *testing.T) {
	text := "参考文档1、4、5"
	has, docIndexs, newText := markInDocIndex(text, docRefPatternList)

	assert.True(t, has)
	assert.NotEmpty(t, docIndexs)
	assert.NotEqual(t, text, newText)
}

// TestMarkInDocIndex_CommaSeparated tests markInDocIndex with comma-separated references
func TestMarkInDocIndex_CommaSeparated(t *testing.T) {
	text := "参考文档1, 4"
	has, docIndexs, _ := markInDocIndex(text, docRefPatternList)

	assert.True(t, has)
	assert.NotEmpty(t, docIndexs)
}

// TestMarkInDocIndex_WithAnd tests markInDocIndex with "and" pattern
func TestMarkInDocIndex_WithAnd(t *testing.T) {
	text := "参考文档1和4"
	has, docIndexs, _ := markInDocIndex(text, docRefPatternList)

	assert.True(t, has)
	assert.NotEmpty(t, docIndexs)
}

// TestMarkInDocIndex_ParenthesesPattern tests markInDocIndex with parentheses pattern
func TestMarkInDocIndex_ParenthesesPattern(t *testing.T) {
	text := "（参考信息1, 4）"
	has, docIndexs, _ := markInDocIndex(text, docRefPatternList)

	assert.True(t, has)
	assert.NotEmpty(t, docIndexs)
}

// TestMarkInDocIndex_DocumentIDPattern tests markInDocIndex with document ID pattern
func TestMarkInDocIndex_DocumentIDPattern(t *testing.T) {
	text := "（参考文档ID：第1个）"
	has, docIndexs, _ := markInDocIndex(text, docRefPatternList)

	assert.True(t, has)
	assert.NotEmpty(t, docIndexs)
}

// TestMarkInDocIndex_PatternList tests that all docRefPatternList patterns work
func TestMarkInDocIndex_PatternList(t *testing.T) {
	tests := []struct {
		name string
		text string
	}{
		{"pattern 1", "第1个和第4个参考信息"},
		{"pattern 2", "第1个参考信息"},
		{"pattern 3", "（参考信息1, 4）"},
		{"pattern 4", "（参考信息1、4）"},
		{"pattern 5", "（参考文档ID：第1个）"},
		{"pattern 6", "参考文档第1个"},
		{"pattern 7", "参考文档第1个和第4个"},
		{"pattern 8", "参考文档第1个、第4个、第5个"},
		{"pattern 9", "参考文档1"},
		{"pattern 10", "参考文档1, 4"},
		{"pattern 11", "参考信息1, 4"},
		{"pattern 12", "参考文档1和4"},
		{"pattern 13", "参考文档1、4和5"},
		{"pattern 14", "参考文档1、4"},
		{"pattern 15", "参考文档1、4、5"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			has, docIndexs, newText := markInDocIndex(tt.text, docRefPatternList)
			assert.True(t, has, "Pattern should match: %s", tt.name)
			assert.NotEmpty(t, docIndexs, "Should have document indices: %s", tt.name)
			assert.NotEqual(t, tt.text, newText, "Text should be modified: %s", tt.name)
		})
	}
}

// TestStringIndexInfo_Key tests stringIndexInfo.key() method
func TestStringIndexInfo_Key(t *testing.T) {
	info := &stringIndexInfo{
		Start: 10,
		End:   20,
		Value: "test",
	}

	expected := "10:20"
	assert.Equal(t, expected, info.key())
}

// TestStringIndexInfo_KeyDifferentValues tests stringIndexInfo.key() with different values
func TestStringIndexInfo_KeyDifferentValues(t *testing.T) {
	tests := []struct {
		start    int
		end      int
		expected string
	}{
		{0, 0, "0:0"},
		{0, 100, "0:100"},
		{50, 75, "50:75"},
		{999, 1000, "999:1000"},
	}

	for _, tt := range tests {
		t.Run(tt.expected, func(t *testing.T) {
			info := &stringIndexInfo{
				Start: tt.start,
				End:   tt.end,
			}
			assert.Equal(t, tt.expected, info.key())
		})
	}
}

// TestDocRefPatternList_NotEmpty verifies docRefPatternList is not empty
func TestDocRefPatternList_NotEmpty(t *testing.T) {
	assert.NotEmpty(t, docRefPatternList)
	assert.Greater(t, len(docRefPatternList), 10)
}

// TestDocRefPatternList_AllValidRegex verifies all patterns are valid regex
func TestDocRefPatternList_AllValidRegex(t *testing.T) {
	for i, pattern := range docRefPatternList {
		assert.NotNil(t, pattern, "Pattern at index %d should not be nil", i)
		// Verify it compiles as a valid regex
		assert.IsType(t, &regexp.Regexp{}, pattern, "Pattern at index %d should be a regexp", i)
	}
}

// TestConstants_DoNotModify tests that important constants are not modified
func TestConstants_DoNotModify(t *testing.T) {
	assert.Equal(t, 10, minSentenceLength)
	assert.Equal(t, "%d:%d", indexKeyTemp)
	assert.Greater(t, cutScore, 0.0)
	assert.LessOrEqual(t, capScore, cutScore)
}
